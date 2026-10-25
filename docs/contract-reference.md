# Contract reference — K4 chi-square contingency tables

Source: [`CONTRACT.md` v1.0.0](https://gist.github.com/seyyah/08d3e031781d853b17366be8ba264211)

This is a working summary of the instructor's CLI contract for the assigned family. It does not describe the behavior discovered in G*Power; those findings belong in `SPEC.md` and `LEDGER.md` after REA investigation.

## Test family

- Test ID: `chi2-contingency`
- G*Power selection: `χ² tests` → `Goodness-of-fit tests: Contingency tables`
- Clinical example: treatment response rates
- Required modes for the sprint: `a-priori`, `post-hoc`
- Bonus modes: `compromise`, `criterion`, `sensitivity`

## Inputs and outputs

| Mode | Required inputs | Required output fields |
|---|---|---|
| `a-priori` | `w`, `alpha`, `power`, `df` | `ncp`, `critical_chi2`, `n_total`, `actual_power` |
| `post-hoc` | `w`, `alpha`, `n_total`, `df` | `ncp`, `critical_chi2`, `power` |
| `compromise` | `w`, `beta_alpha_ratio`, `n_total`, `df` | `ncp`, `critical_chi2`, `alpha`, `beta`, `power` |
| `criterion` | `w`, `power`, `n_total`, `df` | `ncp`, `critical_chi2`, `alpha` |
| `sensitivity` | `alpha`, `power`, `n_total`, `df` | `ncp`, `critical_chi2`, `w` |

`w` is effect size; `df` is an input for this family, not an output; `critical_chi2` is the critical chi-square value. The sprint's mandatory deliverable only requires the first two modes.

## CLI and output rules

- Command form: `gpower-clone --test chi2-contingency --mode <MODE> --<field> <value> ...`.
- No defaults: every input required by the selected mode must be supplied.
- Unknown fields and fields irrelevant to the selected mode are errors.
- Decimal separator is a dot. Calls must be deterministic, offline, and complete within 2 seconds.
- Success: one-line JSON on stdout, exit code 0. Numeric outputs use full double precision; integer outputs are JSON integers.
- Invalid input: one-line JSON containing `error`, with exit code 2. Contract error codes include `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED`, and `NO_SOLUTION`.

## Contract ranges for this family

- `alpha`, `power`: strictly between 0 and 1.
- `w`: greater than 0.
- `n_total`: integer at least 2.
- `df`: integer at least 1.

The contract defines the interface and these ranges. It does not specify the observed rounding/search behavior of G*Power; investigate and document that behavior with REA evidence.
