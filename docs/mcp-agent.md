# MCP server and natural-language agent

## Server

The stdio MCP server is `gpower_clone.mcp_server`. It implements newline-delimited JSON-RPC requests, advertises `2026-07-28` through `server/discover`, and supports the `2025-11-25` initialize handshake for older clients. The version negotiation and tool result fields follow the [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28/server/discover) and its [tool-call contract](https://modelcontextprotocol.io/specification/2026-07-28/server/tools). It exposes two deterministic tools:

| Tool | Required inputs | Engine result |
|---|---|---|
| `chi2_contingency_a_priori` | `w`, `alpha`, `power`, `df` | `ncp`, `critical_chi2`, `n_total`, `actual_power` |
| `chi2_contingency_post_hoc` | `w`, `alpha`, `n_total`, `df` | `ncp`, `critical_chi2`, `power` |

The handlers call `engine.a_priori` and `engine.post_hoc` directly. There is no second implementation of the statistical calculation.

An MCP host should launch the installed module over stdio. For example, on Windows:

```json
{
  "mcpServers": {
    "gpower-ki-kare": {
      "command": "C:\\path\\to\\project\\.venv\\Scripts\\python.exe",
      "args": ["-m", "gpower_clone.mcp_server"]
    }
  }
}
```

Install the project into that interpreter first with `python -m pip install -e .`.

## Natural-language agent

Install the optional OpenAI dependency using `python -m pip install -e ".[agent]"`, set `OPENAI_API_KEY` in the user's environment, and invoke `gpower-agent "..."`. `GPOWER_AGENT_MODEL` optionally selects a different chat-completions model; the default is `gpt-4.1-mini`.

The agent discovers tools from its local MCP child process, offers their schemas to the model as function tools, calls the selected MCP tool, and gives the returned engine JSON back to the model for a Turkish explanation. The model is instructed to ask for missing inputs and never invent defaults. No API key is written to project files.

## Verification record

- The MCP stdio session negotiated the `2026-07-28` discovery path.
- `tools/list` returned both K4 tools.
- `tools/call` for `w=0.3`, `alpha=0.05`, `n_total=100`, `df=5` returned `ncp=9`, `critical_chi2=11.070497693516401`, and `power=0.6235846116825671`.
- The live language-model request is not verified in this workspace because no OpenAI key was supplied for this run.
