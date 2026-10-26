# K4 GUI observations

## A-priori reference run

- Source: user-provided screenshot of G*Power 3.1.9.7, captured during the current desktop session.
- Selection: `χ² tests` → `Goodness-of-fit tests: Contingency tables`; `A priori: Compute required sample size – given α, power, and effect size`.
- Inputs visibly shown: `w = 0.3`, `α err prob = 0.05`, `Power (1−β err prob) = 0.95`, `df = 5`.
- Outputs visibly shown: noncentrality parameter `λ = 19.8000000`, critical `χ² = 11.0704977`, total sample size `N = 220`, actual power `0.9502155`.
- Screenshot: [`k4-apriori-reference.png`](k4-apriori-reference.png).
- Evidence status: manual GUI observation supplied by the user. This is useful as a working reference, but is **not REA-tagged evidence** and must not be cited as such for the assignment's scoring requirement.
- Cross-check: the displayed values match the K4 public a-priori vector in `oracle/public_vectors.jsonl`.

## Post-hoc reference run

- Source: user-provided screenshot of G*Power 3.1.9.7, captured during the current desktop session.
- Selection: `χ² tests` → `Goodness-of-fit tests: Contingency tables`; `Post hoc: Compute achieved power – given α, sample size, and effect size`.
- Inputs visibly shown: `w = 0.3`, `α err prob = 0.05`, `Total sample size = 100`, `df = 5`.
- Outputs visibly shown: noncentrality parameter `λ = 9.0000000`, critical `χ² = 11.0704977`, power `0.6235846`.
- Screenshot: [`k4-posthoc-reference.png`](k4-posthoc-reference.png).
- Evidence status: manual GUI observation supplied by the user; not REA-tagged evidence.
- Cross-check: the displayed values match the K4 public post-hoc vector in `oracle/public_vectors.jsonl`.

## Post-hoc fractional-df probe

- Probe: changed only `df` from 5 to 1.5 in the post-hoc reference run (`w=0.3`, `alpha=0.05`, `n_total=100`).
- Observed: G*Power accepted the fractional `df` and calculated results rather than rejecting the input.
- Outputs visibly shown: `lambda = 9.0000000`, `critical_chi2 = 4.9801953`, `power = 0.8071182`.
- Screenshot: [`k4-posthoc-fractional-df-1.5.png`](k4-posthoc-fractional-df-1.5.png).
- Evidence status: manual GUI observation supplied by the user; this is a candidate undocumented behavior, not REA-tagged evidence.
- Scope note: the sprint CLI contract specifies integer `df`; this probe records observed G*Power UI behavior and does not override the required CLI validation contract.

## A-priori sample-size boundary probe

- Probe: kept the chi-square contingency-table post-hoc inputs at `w=0.3`, `alpha=0.05`, `df=5`, changed `n_total` to 219, and recalculated in G*Power 3.1.9.7.
- Observed output: `lambda = 19.7100000`, `critical chi-square = 11.0704977`, and power `0.9492324`.
- Comparison: the a-priori run at `N=220` reports power `0.9502155` for a target of 0.95. Thus N=219 is below the target and N=220 is at or above it for this vector.
- Independent CLI calculation: N=219 power `0.9492324309108173`; N=220 power `0.9502155018970154`; a-priori returns `N=220` and the same actual power.
- Evidence status: G*Power run is a GUI observation, not REA-tagged evidence. The CLI values are direct outputs of the clean-room engine. This single boundary probe supports minimality for this public vector only; it does not prove the hidden-vector threshold.
