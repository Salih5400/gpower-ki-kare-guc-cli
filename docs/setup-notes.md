# Setup notes

All downloaded archives remain in the user's Downloads folder. Extracted tools are under `work/tools/`, which `.gitignore` excludes from the repository.

| Tool | Extracted path | Version / identity |
|---|---|---|
| G*Power | `work/tools/gpower/GPower_3.1.9.7_143/GPowerNT.exe` | 3.1.9.7, file SHA-256 `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` |
| Ghidra | `work/tools/ghidra/ghidra_12.1.4_PUBLIC` | 12.1.4, official release ZIP SHA-256 `DDAC49F903DA9D5BAC833E5CC79395098B9C33CFD3279BE5F31BD00387D2D4DB` |
| Temurin JDK | `work/tools/jdk/jdk-21.0.12.1+1` | OpenJDK 21.0.12.1+1, ZIP SHA-256 `F9D6E191AB098C0D416E7D588A24420A8621CD2F4720DAB2459B8B7B2D2D8B4E` |

The Ghidra ZIP hash matches the checksum published with the official [Ghidra 12.1.4 release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build).

An earlier programmatic launch attempt reported `ERROR_ILLEGAL_DLL_RELOCATION` (0x26F). The user subsequently opened G*Power from the desktop and supplied the reference runs documented in `logs/gui-observations.md`; the earlier launch error was therefore not a blocker. Do not change Windows system DLLs to work around it.

The extracted tool paths are relative to the project root:

- `GHIDRA_INSTALL_DIR=work/tools/ghidra/ghidra_12.1.4_PUBLIC`
- `JAVA_HOME=work/tools/jdk/jdk-21.0.12.1+1`

The installed REA CLI works with the bundled Node.js 24 runtime when those variables are supplied to the process. As of 2026-10-26, the connected REA MCP server still reports `GHIDRA_INSTALL_DIR` as unset, so use the CLI route for analysis until the server environment is corrected. `work/` is ignored and must not be committed; it contains the binary, analysis scratch files, and extracted tools.
