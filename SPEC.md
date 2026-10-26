# K4 reconstruction specification: chi-square contingency tables

Status: inspection draft for clean-room implementation. Required modes are `a-priori` and `post-hoc` only. This specification combines the instructor's interface contract with observed G*Power behavior; evidence tags distinguish those sources.

## Evidence key

- `[DOK]` Instructor's `CONTRACT.md` v1.0.0, summarized in `docs/contract-reference.md`.
- `[REA]` Static evidence from the exact G*Power 3.1.9.7 binary, listed in `LEDGER.md`.
- `[AJAN]` Analyst interpretation of the evidence. Treat as provisional where marked.

## Interface

- The program is named `gpower-clone`. `[DOK]`
- Required command form: `gpower-clone --test chi2-contingency --mode <MODE> --<field> <value> ...`. `[DOK]`
- `--test` must be `chi2-contingency`; required modes are `a-priori` and `post-hoc`. `[DOK]`
- Every input required for the selected mode must be present. There are no defaults. Unknown fields and fields irrelevant to the selected mode are errors. `[DOK]`
- Parse decimal values with `.` as the decimal separator. Reject non-finite values. Calls are deterministic, offline, and must complete within two seconds. `[DOK]`
- A successful call writes one JSON object on one line to stdout and exits 0. Return full-precision double values and JSON integers for integer fields. `[DOK]`
- An invalid call writes one JSON object containing `error` on one line and exits 2. Use the contract's codes: `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED`, and `NO_SOLUTION`. `[DOK]`

## Shared statistical model

- Inputs `w`, `alpha`, `power`, and `df` have the contract ranges: `w > 0`, `0 < alpha < 1`, `0 < power < 1`, integer `df >= 1`. For post-hoc, `n_total` is an integer `>= 2`. Reject NaN and infinities. `[DOK]`
- The contingency-table power analysis uses a central chi-square critical value at cumulative probability `1 - alpha`. `[REA]` `FUN_004e5310` calls the chi-square quantile path with `1 - param_4`; `FUN_0043f050` numerically solves the CDF for its target probability. The mapping of `param_4` to the UI's alpha is supported by the observed critical value `11.0704977` for `alpha=.05, df=5`. `[AJAN]`
- The alternative distribution is noncentral chi-square with noncentrality `lambda = N * w^2`; power is its upper-tail probability above the critical value. `[AJAN]` This is consistent with the displayed values (`N=220, w=.3 -> lambda=19.8`; `N=100, w=.3 -> lambda=9`) and with the REA-observed CDF/quantile paths and complementary-tail calculation. The exact K4 class-to-parameter data flow remains an open static-analysis question; see `LEDGER.md`.
- Calculate `critical_chi2` once from `df` and `alpha`, then use the same value for either mode. `[REA]/[AJAN]`

## Acceptance criteria

### A-priori

- Given `w`, `alpha`, `power`, and `df`, compute the smallest integer total sample size `N >= 2` whose achieved upper-tail power is at least the requested power. Return `ncp = N*w^2`, `critical_chi2`, integer `n_total`, and achieved power as `actual_power`. `[DOK]` output names; the REA-observed G*Power path solves `Power(w, alpha, N) - target_power = 0` for continuous N, then conditionally stabilizes to 10 decimal places and applies `ceil`. The GUI path's flag controlling this postprocessing is not yet resolved. For the clean-room engine, monotone integer search is equivalent on the supported domain and was used to return the smallest passing integer. `[REA]/[AJAN]`
- For `w=.3`, `alpha=.05`, `power=.95`, and `df=5`, return `ncp=19.8`, `critical_chi2` rounding to `11.0704977`, `n_total=220`, and `actual_power` rounding to `.9502155`. `[DOK]` public vector, corroborated by the user-supplied G*Power screenshot `[AJAN]`.

### Post-hoc

- Given `w`, `alpha`, `n_total`, and `df`, compute `ncp=n_total*w^2`, the central critical value, and achieved upper-tail power. Return fields `ncp`, `critical_chi2`, and `power`. `[DOK]` field names; model interpretation `[AJAN]`.
- For `w=.3`, `alpha=.05`, `n_total=100`, and `df=5`, return `ncp=9`, `critical_chi2` rounding to `11.0704977`, and `power` rounding to `.6235846`. `[DOK]` public vector, corroborated by the user-supplied G*Power screenshot `[AJAN]`.

### Input errors

- A missing mode-specific input returns `MISSING_PARAM`. `[DOK]`
- An unrecognized option returns `UNKNOWN_PARAM`; a recognized option belonging only to another mode is also an error (use `UNKNOWN_PARAM` unless the contract's examples specify otherwise). `[DOK]`
- A malformed number, non-finite number, or non-integer supplied for an integer field returns `INVALID_VALUE`. A finite numeric value outside the declared range returns `OUT_OF_RANGE`. `[DOK]`
- Search integer sample sizes only through `N=10,000,000` inclusive. If no solution is found in `[2, 10,000,000]`, return `NO_SOLUTION`; do not silently clamp a result. This is a documented implementation bound, not a claim about G*Power's internal limit. `[AJAN]`

## Numerical implementation notes

- Implement the calculation in one reusable engine; CLI parsing/JSON output are a thin adapter. `[DOK]`
- The `PowerChiCont` class is registered in the power-class registry. Its calculation path uses `lambda = N*w^2`, `critical_chi2 = chi2_quantile(1-alpha, df)`, and `power = 1 - noncentral_chi2_cdf(critical_chi2, df, lambda)`. `[REA]` See `LEDGER.md` for evidence IDs and limitations.
- G*Power's K4 a-priori path selects the sample-size callback `Power(w_fixed, alpha_fixed, N) - target_power`; its shared bracketed root solver uses tolerance `1e-10` and a 300-iteration cap on that path. A separate mode solves for `w` with N fixed and a 100-iteration cap. `[REA]`
- When the a-priori solver's round-up flag is nonzero, it transforms the root as `ceil(floor(root*1e10 + 0.5)/1e10)`. The flag value passed by the visible GUI path is unresolved. `[REA]`
- Public-vector comparisons should use the contract's seven-decimal expected values as the initial compatibility target; emitted JSON still uses full double precision. Exact hidden-vector threshold is determined by the sprint grader. `[DOK]`

## Unresolved behavior

- Which GUI/UI call path reaches the registered `PowerChiCont` class and what value it supplies for the optional round-up flag.
- Exact solver bracket initialization and lower-bound semantics for the visible GUI a-priori path, beyond the observed 300-iteration cap and root callback.
- Error code/message mapping for every invalid boundary and overflow case.
- Whether the seven-decimal G*Power display is rounded or truncated. CLI contract requires full precision, so display formatting is not copied.

Do not promote unresolved items to `[REA]` claims without new evidence. The supplemental GUI screenshots are not REA-tagged evidence.
