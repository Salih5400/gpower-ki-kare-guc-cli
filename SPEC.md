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

- Given `w`, `alpha`, `power`, and `df`, compute the smallest integer total sample size `N >= 2` whose achieved upper-tail power is at least the requested power. Return `ncp = N*w^2`, `critical_chi2`, integer `n_total`, and achieved power as `actual_power`. `[DOK]` output names; minimal-integer search is a provisional interpretation `[AJAN]` and must remain easy to revise if further REA evidence contradicts it.
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
- The binary has an observed CDF helper with Poisson-distribution and chi-square-distribution objects, a CDF quantile wrapper, and a derivative-assisted safeguarded root solver. `[REA]` See `LEDGER.md` for evidence IDs and limitations. The solver accepts target probability in `[0,1]`, returns 0 at 0 and `+infinity` at 1, and uses relative/probability stopping thresholds around `1e-10`. These details concern G*Power's internal distribution solver; they do not, by themselves, establish the K4 sample-size search algorithm. `[REA]`
- Public-vector comparisons should use the contract's seven-decimal expected values as the initial compatibility target; emitted JSON still uses full double precision. Exact hidden-vector threshold is determined by the sprint grader. `[DOK]`

## Unresolved behavior

- Exact K4 call path from `CEff_CHI_GoF_Cont` / `PowerChiCont` to the distribution and sample-size calculations.
- How the a-priori mode searches `N`, including initialization, bounds, monotonicity assumptions, and exact minimality/termination.
- Exact parameter mapping into noncentrality and CDF calls, beyond consistency with `lambda=N*w^2` and the displayed public values.
- Error code/message mapping for every invalid boundary and overflow case.
- Whether the seven-decimal G*Power display is rounded or truncated. CLI contract requires full precision, so display formatting is not copied.

Do not promote unresolved items to `[REA]` claims without new evidence. The supplemental GUI screenshots are not REA-tagged evidence.
