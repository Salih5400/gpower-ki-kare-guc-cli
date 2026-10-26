"""Small MCP stdio server backed by the shared calculation engine.

This server speaks the newline-delimited JSON-RPC MCP stdio transport and the
2025-11-25 initialize/tools protocol. It has no runtime dependency on an MCP SDK.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .engine import a_priori, post_hoc


_PROTOCOL_VERSION = "2025-11-25"
_TOOLS = [
    {
        "name": "chi2_contingency_a_priori",
        "description": "Find minimum total sample size for a chi-square contingency-table test.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "w": {"type": "number", "description": "Cohen effect size w; must be greater than zero."},
                "alpha": {"type": "number", "description": "Type-I error probability; strictly between zero and one."},
                "power": {"type": "number", "description": "Desired power; strictly between zero and one."},
                "df": {"type": "integer", "description": "Degrees of freedom; integer at least one."},
            },
            "required": ["w", "alpha", "power", "df"],
            "additionalProperties": False,
        },
    },
    {
        "name": "chi2_contingency_post_hoc",
        "description": "Calculate achieved power for a chi-square contingency-table test.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "w": {"type": "number", "description": "Cohen effect size w; must be greater than zero."},
                "alpha": {"type": "number", "description": "Type-I error probability; strictly between zero and one."},
                "n_total": {"type": "integer", "description": "Total sample size; integer at least two."},
                "df": {"type": "integer", "description": "Degrees of freedom; integer at least one."},
            },
            "required": ["w", "alpha", "n_total", "df"],
            "additionalProperties": False,
        },
    },
]


def _response(request_id: Any, result: dict[str, Any], modern: bool = False) -> dict[str, Any]:
    if modern:
        result.setdefault("resultType", "complete")
        result["_meta"] = {"io.modelcontextprotocol/serverInfo": {"name": "gpower-ki-kare-guc-cli", "version": "0.1.0"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_call(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments") or {}
    if name == "chi2_contingency_a_priori":
        required = {"w", "alpha", "power", "df"}
        calculate = lambda: a_priori(args["w"], args["alpha"], args["power"], args["df"])
    elif name == "chi2_contingency_post_hoc":
        required = {"w", "alpha", "n_total", "df"}
        calculate = lambda: post_hoc(args["w"], args["alpha"], args["n_total"], args["df"])
    else:
        raise KeyError(f"Unknown MCP tool: {name}")

    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be an object")
    if set(args) != required:
        missing = sorted(required - set(args))
        extra = sorted(set(args) - required)
        raise ValueError(f"Invalid arguments; missing={missing}, extra={extra}")
    for numeric_name in (required - {"df", "n_total"}):
        value = args[numeric_name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{numeric_name} must be a number")
    for integer_name in (required & {"df", "n_total"}):
        if type(args[integer_name]) is not int:
            raise ValueError(f"{integer_name} must be an integer")
    try:
        result = calculate()
    except (ArithmeticError, OverflowError, TypeError, ValueError) as exc:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(exc)})}], "isError": True}
    return {"content": [{"type": "text", "text": json.dumps(result, separators=(",", ":"), allow_nan=False)}]}


def _handle(message: dict[str, Any], initialized: bool) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    metadata = params.get("_meta") or {}
    requested_version = metadata.get("io.modelcontextprotocol/protocolVersion")
    modern = requested_version == "2026-07-28"

    if method == "notifications/initialized" or method == "notifications/cancelled":
        return None
    if method == "ping":
        return _response(request_id, {}, modern)
    if method == "server/discover":
        return _response(
            request_id,
            {
                "resultType": "complete",
                "supportedVersions": ["2026-07-28", _PROTOCOL_VERSION],
                "capabilities": {"tools": {}},
                "instructions": "K4 chi-square contingency-table power analysis. Use the calculation tools for numeric results.",
                "ttlMs": 300000,
                "cacheScope": "public",
            },
            True,
        )
    if method == "initialize":
        requested = params.get("protocolVersion", _PROTOCOL_VERSION)
        version = requested if requested in {"2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"} else _PROTOCOL_VERSION
        return _response(
            request_id,
            {
                "protocolVersion": version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "gpower-ki-kare-guc-cli", "version": "0.1.0"},
                "instructions": "K4 chi-square contingency-table power analysis. Use the calculation tools for numeric results.",
            },
        )
    if not initialized:
        return _error(request_id, -32002, "Server is not initialized")
    if requested_version not in (None, "2026-07-28"):
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32022, "message": "Unsupported protocol version", "data": {"requested": requested_version, "supported": ["2026-07-28", _PROTOCOL_VERSION]}}}
    if method == "tools/list":
        result = {"tools": _TOOLS}
        if modern:
            result.update({"ttlMs": 300000, "cacheScope": "public"})
        return _response(request_id, result, modern)
    if method == "tools/call":
        try:
            result = _tool_call(params)
        except KeyError as exc:
            return _error(request_id, -32602, str(exc))
        except (TypeError, ValueError) as exc:
            result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
        return _response(request_id, result, modern)
    if request_id is None:
        return None
    return _error(request_id, -32601, f"Method not found: {method}")


def main() -> None:
    initialized = False
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                response = _error(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid JSON-RPC request")
            else:
                if message.get("method") == "initialize" or (message.get("params") or {}).get("_meta", {}).get("io.modelcontextprotocol/protocolVersion") == "2026-07-28":
                    initialized = True
                response = _handle(message, initialized)
        except json.JSONDecodeError:
            response = _error(None, -32700, "Parse error")
        except Exception as exc:  # Keep the stdio stream alive on one malformed call.
            request_id = message.get("id") if isinstance(message, dict) else None
            response = _error(request_id, -32603, f"Internal error: {exc}")
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":"), ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
