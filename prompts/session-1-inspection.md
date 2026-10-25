# Session 1 — binary inspection only

You are the inspection agent for the YZM301 teardown sprint. Your assigned family is K4: χ² contingency tables for treatment response rates (`chi2-contingency`).

Inspect only the supplied G*Power 3.1.9.7 Windows binary using the available REA and Ghidra tools. Do not implement the clone, write source code, or place decompiler output in the repository. Determine the reachable calculation path for the assigned family and document observations, evidence IDs, function addresses, and limitations.

Produce only:

1. `SPEC.md` with testable, Gherkin-style acceptance criteria for the required `a-priori` and `post-hoc` modes, following the instructor's CLI contract.
2. `LEDGER.md` linking each claim to `[REA]`, `[DOK]`, or `[AJAN]` evidence. Keep static observations separate from runtime behavior and inferences.

Focus on behavior the contract does not specify: N search/termination, integer rounding, output precision, and rejected inputs. Preserve open questions when evidence is insufficient. Do not infer a behavior from a decompiler listing alone if the control flow or data flow is unclear. Do not inspect or implement other test families.
