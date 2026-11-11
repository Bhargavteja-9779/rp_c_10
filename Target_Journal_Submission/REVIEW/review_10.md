# Review round 10 — Final adversarial review (attempting to reject)

Version: final strict build (all tokens resolved from results; audit `final_audit_checks.json`).
Approach: re-read title, abstract, methods, results, discussion against result files; look for one fatal flaw, then major/moderate/minor issues not raised in rounds 1–9.

## Search for a fatal flaw
Candidates examined and **not** found fatal:
1. *Leakage between development and external data* — recording/window fingerprint audit; no shared patients; external cohorts never used for fitting/calibration/selection (verified in `run_main.py`, `run_revision.py`, `run_smoother_check.py`: all selection on calA/calB/dev_test).
2. *Result fabrication / hand-typed numbers* — strict build resolves 166 tokens from result files; remaining literals are design constants or verified counts.
3. *Primary hypothesis failure hidden* — reported in Abstract, Results and Limitations.
4. *Post-hoc method selection presented as confirmatory* — A1 disclosed with the quick-check exposure; R1 and other analyses labelled post hoc.
No fatal flaw found. The most damaging legitimate criticism remains **limited novelty** (the effective method is an HMM smoother whose accuracy advantage over a tuned median filter is small) — a judgement call for the editor rather than a flaw.

## Major
| # | Issue | Fix |
|---|---|---|
| 10.1 | "Amendment A1, applied before the full analysis" is inaccurate: the rule was *specified* before the full run but *evaluated* on development results of the full run (computed together with the external results, which were not used). | Reworded in Abstract, Results and Supplement: "selected by a rule specified before the full analysis and evaluated on development patients only". |
| 10.2 | Abstract uses the abbreviation "PA-HMMQ" (journal: avoid abbreviations in abstract). | Removed from abstract. |

## Moderate
| # | Issue | Fix |
|---|---|---|
| 10.3 | In patients with >50% burden the final method is worse than the calibrated-emission variant (Table S6). | Now reported in Results and Discussion (trade-off across the burden spectrum). |
| 10.4 | Practical recommendation missing: since adaptation adds nothing, the simpler fixed-dynamics HMM with probability emissions is sufficient. | Sentence added to Clinical implications. |
| 10.5 | Equations rendered as inline text (no equation objects). | Acceptable under the journal's format-free first submission; flagged for typesetting. |
| 10.6 | Author names, affiliations, funding, conflicts, repository URL are placeholders. | Cannot be completed by the analysis team; flagged in the risk report. |

## Minor
* 10.7 Figure 6 joins categorical strata with lines — legend states lines are for readability. ✓
* 10.8 Robustness evaluated in one external cohort (SHDB-AF). Stated in Methods. ✓
* 10.9 RRNet efficiency figure re-measured on an idle machine (120 ms/24 h vs 12.8 s under contention earlier). ✓
* 10.10 Reference 37/38 (PhysioNet dataset DOIs, arXiv preprint) formatted as "[dataset/preprint]" — acceptable in Vancouver; journal staff may restyle.

---
# Author response (round 10)
10.1, 10.2, 10.4 fixed in text; 10.3 fixed in round-9/10 edits; 10.5–10.6 documented in rejection-risk report.
