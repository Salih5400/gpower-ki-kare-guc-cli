# Chi-square contingency-table power CLI

This is an educational clean-room reimplementation for the YZM301 teardown sprint, assigned family K4 (`chi2-contingency`). It is not G*Power and is not affiliated with its authors.

## Status

- Project folder and contract summary initialized.
- The five public K4 vectors from contract v1.0.0 are in `oracle/public_vectors.jsonl`.
- G*Power 3.1.9.7, Ghidra 12.1.4, and Temurin JDK 21 are downloaded and extracted under the ignored `work/tools/` folder.
- The Ghidra release ZIP SHA-256 matches the hash published on the official Ghidra release page.
- `GPowerNT.exe` SHA-256: `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`.
- G*Power 3.1.9.7 is now confirmed running from the user's desktop. User-provided a-priori and post-hoc reference runs match the two public K4 vectors; see `logs/gui-observations.md` and the screenshots there.
- An earlier programmatic launch attempt reported `ERROR_ILLEGAL_DLL_RELOCATION` (0x26F). That did not prevent the user from opening G*Power interactively.
- Ghidra 12.1.4 and JDK 21 are healthy under the installed REA CLI when run with Node 24.22.1 and the user-level `GHIDRA_INSTALL_DIR` / `JAVA_HOME` values. The connected MCP server still reports Ghidra unconfigured; the REA CLI is the working analysis path for now.
- Initial REA findings and Evidence IDs are recorded in `LEDGER.md`. Raw JSON stays in ignored `work/rea/`; no decompiler output is checked in. The manual screenshots remain supplementary, not REA-tagged evidence.
- `SPEC.md` is the inspection draft for the required CLI modes. It clearly marks the formulas and minimum-N search behavior that still need direct K4-path corroboration.
- A further REA analysis of `FUN_0043f050` found G*Power's CDF inverse uses a derivative-assisted bounded step with midpoint fallback and thresholds near `1e-10`; see the Evidence ID and limits in `LEDGER.md`.
- A separate clean-room session implemented the required Python CLI and reusable calculation engine from `SPEC.md` only. The required public a-priori and post-hoc vectors were run and match the expected values to seven decimal places. No separate automated test suite has been added; see `src/` and `pyproject.toml` for the implementation and launch options.
- An extra G*Power GUI boundary probe at `N=219` produced power `0.9492324`; the CLI gives `0.9492324309108173`. At `N=220`, both produce `0.9502155018970154`, so the a-priori result is the first passing N for this public vector. This does not establish the hidden-vector pass rate.
- The MCP stdio server and Turkish natural-language agent are implemented in `src/gpower_clone/`. A local MCP client smoke check listed both tools and called the post-hoc tool successfully. The live OpenAI model call remains unverified because no API key was supplied for this run.

## Scope

Implement only the K4 chi-square contingency-table family. Required modes are `a-priori` and `post-hoc`; the other modes are optional bonuses. Follow the instructor's [`CLI contract`](https://gist.github.com/seyyah/08d3e031781d853b17366be8ba264211) and put behavior inferred from the binary in `SPEC.md` / `LEDGER.md` with evidence labels.

## MCP and natural-language agent

The same engine is exposed through an MCP stdio server and a Turkish natural-language agent. The MCP server has no third-party runtime dependency. Python 3.10 or newer is required; only the AI agent needs the OpenAI client library:

```powershell
python -m pip install -e ".[agent]"
gpower-mcp
```

Configure `gpower-mcp` in an MCP host using the Python executable and module command `-m gpower_clone.mcp_server`. The server speaks MCP stdio, supports protocol discovery for `2026-07-28` clients and the `2025-11-25` initialize handshake, and exposes `chi2_contingency_a_priori` and `chi2_contingency_post_hoc`. Tool calls invoke the same engine as the CLI.

For the standalone agent, set `OPENAI_API_KEY` in your local environment, then run:

```powershell
gpower-agent "w=0.3, alpha=0.05, güç=0.95 ve df=5 için kaç denek gerekir?"
```

The model only selects and explains calls; all numerical calculations go through the shared MCP engine. The API key is read from the environment and is not stored by the application.

## Required attribution

G*Power is by Faul, Erdfelder, Lang, and Buchner (2007, 2009). This project does not include GPower.exe or decompiler output.
