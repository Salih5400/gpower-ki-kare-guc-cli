# K4 evidence ledger

Target: G*Power 3.1.9.7 `GPowerNT.exe`, SHA-256 `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`.

Analysis route: REA CLI 6.5.0 under Node.js 24.22.1 and Ghidra 12.1.4. The CLI evidence JSON is retained locally under the ignored `work/rea/` directory. No decompiler output is checked into the repository.

## REA evidence

| Claim / observation | REA Evidence ID | Status and limits |
|---|---|---|
| Target is a PE x86 executable; Ghidra reports 9,116 procedures and 2,570 defined strings. | `ev_25dc8648aa3000b68205edad20ad76db1a42586346462d3c0558a286ac7ed251` | Observed shipped-artifact identity and inventory. Counts are scoped to Ghidra's defined inventory. |
| The binary contains the strings `CEff_CHI_GoF_Cont`, `PowerChiCont`, `ChiDistribution`, plus `ChiDist-Cdf` / `ChiDist-Quantile` error labels and `chi2cdf`, `chi2inv`, `chi2pdf`. | `ev_7433d93dc0d03b2ac61b670cc68d4826470820c9f25a141a4543826aa7c4060d` | Observed strings only; a string by itself does not prove a call path or behavior. |
| `CEff_CHI_GoF_Cont` has an RTTI/type-metadata reference; the initial reference resolves to metadata, not a calculation function. | `ev_2a01a60a952bc53bfe6fb72acec592ea09abfb135b0430aead2b9ad6b6ed8ba2`, `ev_f06de548502c1d0e39fe6d1085fc92bfef5c1b99cc77fe98b2c36ef1e56cb050` | Observed reference chain. The first reference is data; it must not be described as a function. |
| Literal search for `PowerChiCont` finds only the RTTI name string; the recorded xref query returns no references to that metadata address. | `ev_9ed222dc40738af437c9035ddefdcee45c565a179bb2b6932ab9175ef640f01b`, `ev_810299475e9b5ed9571a6c1414b2984db064896df5aed3a637b9f18ca8e70bfd` | This is a bounded negative observation. It does not prove the class is unused; indirect RTTI/vtable relationships may not be represented by this xref query. K4 calculation ownership remains unresolved. |
| `FUN_00506c30` allocates a `CEff_CHI_GoF_Cont` object, assigns its vtable, and constructs MFC edit/spin controls. | `ev_2512bc2908e0653c31a8ab159ecec681e49f67da3cd14c04a331c989c8990b32` | Observed pseudocode. Supports an effect-size UI component, not power-calculation semantics. |
| `FUN_005066d0` tears down the same class's edit/spin controls. | `ev_48e5483ba338ee56db99a590b11e6c714b4231b5888b50ff922051db05c28eb1` | Observed destructor behavior; not calculation logic. |
| `FUN_0043eca0` is the wrapper containing the `ChiDist-Cdf` error paths and dispatches to `FUN_0043e7e0` for its numeric result. | `ev_bfcbb250ad539c1a608175b6a023e16cafe10c844aaa7a6ca61b836bb96d3e34` | Observed shipped-artifact function body and referenced strings. Parameter roles are not fully recovered. |
| `FUN_0043e7e0` uses `ChiDistribution` and `PoissonDistribution` vtables and accumulates terms in two loops around `floor(param3 / 2)`, with a machine-epsilon stopping check. | `ev_063d699f76105a3c0fe20dfe4f4c207fa40d37d81ff928fb130b2b92b3418b78` | Observed code structure; interpreting it as a Poisson-mixture noncentral chi-square CDF is a derived hypothesis. Exact parameter mapping and mathematical equivalence still need corroboration. |
| `FUN_0043f800` is the `ChiDist-Quantile` wrapper: it sends probability `p` to `FUN_0043f050`, computes `1-p` for the paired-probability validation path, and scales the result by an object field. | `ev_2e2c9c60c865842e6f4a810c63fcd53a0557ac40b3f859a942fc9760c7f8e558` | Observed function body and strings. Caller `FUN_004e5310` passes `1 - param_4`; this is consistent with an upper-tail alpha input, but exact public parameter mapping remains unknown. |
| `FUN_0043f050` numerically inverts the CDF callback `FUN_0043e7e0`: it rejects target probabilities outside `[0,1]`, requires its second argument `>0` and third argument `>=0`, returns `0` at target `0` and `+∞` at target `1`, and otherwise iterates from a distribution-based initial guess. It uses a derivative-assisted step constrained to a factor-of-five interval, then midpoint steps when needed; it stops on probability residual or relative interval thresholds near `1e-10`, and reports a 1000-iteration status. | `ev_5ee1c6e84cc9b1cf9c510105be7dbe908eec8d30061ab5c50c78079dfaf8d8d0` | Observed Ghidra pseudocode/control flow, 967-byte function body. The parameter meanings and exact error-status mapping still need caller/layout corroboration. |
| `FUN_004e5310` constructs a `ChiDistribution`, requests `FUN_0043f800(1 - param_4)`, stores the result, then calls the CDF wrapper and derives a complementary tail value. | `ev_31aab724c171a9084f8984dc8d69e1f0ec3ece6d22b368615324d0b32adef4dd` | Observed call/data flow. Likely a chi-square power/plot routine, but exact ownership by `PowerChiCont` is not established; keep the K4 association as a hypothesis. |
| `FUN_004ea450` calls `FUN_004e5310` inside a range-driven routine. | `ev_58f70dc724aa73284375ce76b3fc297c07975a7b15f2595d4646baa0f9d61f61` | Observed caller. Context looks like plotting/range handling; not used as proof of the core sample-size algorithm. |

## Manual GUI observations (supplementary; not scored as REA evidence)

These user-supplied screenshots are recorded in [`logs/gui-observations.md`](logs/gui-observations.md). The a-priori and post-hoc public vectors match the contract exactly. The `df=1.5` run was accepted by G*Power, but the sprint contract requires integer `df`; this is a candidate out-of-contract GUI behavior only.

## Open questions

- Tie `PowerChiCont` unambiguously to the observed K4 GUI selection and its calculation path.
- Trace a-priori sample-size search, including its integer rounding/termination behavior, from the K4 class to the distribution call.
- Verify how the calculator maps `w`, `N`, and `df` to noncentrality and which tail is used for reported power.
- Resolve whether `FUN_0043f800`'s complement is associated with a lower-tail critical quantile or an upper-tail one; the quantile solver's target and scaling must be reconciled with the observed displayed critical values.
- Probe undocumented boundary/error behavior and keep each result linked to its exact REA Evidence ID. GUI-only observations remain supplementary.
