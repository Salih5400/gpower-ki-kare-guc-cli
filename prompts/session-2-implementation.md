# Session 2 — clean-room implementation only

You are the implementation agent for the YZM301 teardown sprint, assigned family K4: χ² contingency tables (`chi2-contingency`). Implement the CLI and one calculation engine from `SPEC.md` only. Do not read `LEDGER.md`, REA/Ghidra notes, decompiler output, or session 1's conversation. The `SPEC.md` file must fully specify the required behavior and the CLI contract needed for implementation.

Implement the required `a-priori` and `post-hoc` modes. Keep the calculation in one reusable engine; the CLI must be a thin adapter. Do not implement MCP or an AI agent unless separately requested after the CLI passes the required vectors. Never copy G*Power binaries or decompiler output into source files or the repository.
