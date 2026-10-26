"""Natural-language agent that calls the local MCP calculation tools."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """Sen klinik araştırmalarda örneklem büyüklüğü ve istatistiksel güç hesabı için Türkçe yardımcı bir ajansın.
Her sayısal sonucu yerel MCP hesaplama aracını çağırarak üret; sonucu kendin hesaplama veya tahmin etme.
Kullanıcı gerekli parametreleri vermediyse eksikleri kısa ve açık bir soruyla iste; varsayılan değer uydurma.
Sadece desteklenen chi-square contingency-table testinin a-priori ve post-hoc modlarını kullan.
Sonuçta kullanılan girdileri, örneklem büyüklüğünü ve gücü anlaşılır biçimde belirt; hesap motorunun döndürmediği sonuçları ekleme.
Bu araç eğitim amaçlıdır; klinik kararın yerine geçmez."""


class MCPStdioSession:
    """Minimal synchronous MCP stdio client for this single local server."""

    def __init__(self) -> None:
        self._next_id = 1
        self.modern = False
        self._process = subprocess.Popen(
            [sys.executable, "-m", "gpower_clone.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        discovery = self.request("server/discover", {
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                "io.modelcontextprotocol/clientInfo": {"name": "gpower-natural-language-agent", "version": "0.1.0"},
                "io.modelcontextprotocol/clientCapabilities": {},
            }
        })
        self.modern = "2026-07-28" in discovery.get("supportedVersions", [])
        if not self.modern:
            self.request("initialize", {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "gpower-natural-language-agent", "version": "0.1.0"},
            })
            self.notify("notifications/initialized")

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._process.stdin is None or self._process.stdout is None:
            raise RuntimeError("MCP stdio pipes are unavailable")
        request_id = self._next_id
        self._next_id += 1
        request_params = dict(params or {})
        if self.modern and method != "server/discover":
            request_params["_meta"] = {
                "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                "io.modelcontextprotocol/clientInfo": {"name": "gpower-natural-language-agent", "version": "0.1.0"},
                "io.modelcontextprotocol/clientCapabilities": {},
            }
        message = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": request_params}
        self._process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        self._process.stdin.flush()
        while True:
            line = self._process.stdout.readline()
            if not line:
                raise RuntimeError("MCP server closed its output stream")
            response = json.loads(line)
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise RuntimeError(f"MCP {method} failed: {response['error']}")
            return response["result"]

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        if self._process.stdin is None:
            raise RuntimeError("MCP stdio input is unavailable")
        self._process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}, separators=(",", ":")) + "\n")
        self._process.stdin.flush()

    def close(self) -> None:
        if self._process.stdin is not None:
            self._process.stdin.close()
        try:
            self._process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._process.terminate()
            self._process.wait(timeout=3)

    def __enter__(self) -> "MCPStdioSession":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _agent_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"],
            },
        }
        for tool in tools
    ]


def _run(user_text: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ortam değişkeni tanımlı değil.")

    openai = OpenAI(api_key=api_key)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    with MCPStdioSession() as mcp_client:
        tools = _agent_tools(mcp_client.request("tools/list").get("tools", []))
        for _ in range(5):
            response = openai.chat.completions.create(
                model=os.environ.get("GPOWER_AGENT_MODEL", "gpt-4.1-mini"),
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            message = response.choices[0].message
            if not message.tool_calls:
                return message.content or "Gerekli girdiler eksik; lütfen değerleri belirtin."

            messages.append(message.model_dump(exclude_none=True))
            for call in message.tool_calls:
                if call.type != "function":
                    continue
                arguments = json.loads(call.function.arguments)
                result = mcp_client.request(
                    "tools/call",
                    {"name": call.function.name, "arguments": arguments},
                )
                content = "\n".join(
                    item.get("text", "") for item in result.get("content", []) if item.get("type") == "text"
                )
                messages.append({"role": "tool", "tool_call_id": call.id, "content": content})
        raise RuntimeError("Ajan araç çağrısı sınırına ulaştı; isteği sadeleştirip tekrar deneyin.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Kullanım: gpower-agent \"örneklem hesabı için isteğiniz\"")
        raise SystemExit(2)
    try:
        print(_run(" ".join(sys.argv[1:])))
    except Exception as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
