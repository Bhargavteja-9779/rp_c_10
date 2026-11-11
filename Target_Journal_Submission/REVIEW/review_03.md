# Review round 3 — Reviewer #3 (statistical validity, experimental fairness, splitting, leakage)

Version: v1 + rounds 1–2. New issues only.

| # | Severity | Issue | Evidence | Required fix |
|---|---|---|---|---|
| 3.1 | MAJOR | **The development test set is no longer an independent hold-out for the final variant.** Amendment A1 selected the emission model on calB ∪ dev_test. calB is additionally the conformal calibration set. Hence dev_test results (and dev_test coverage) of the final PA-HMMQ are selection-contaminated; only the external cohorts are clean. | S1 §6; Methods | State explicitly in Methods/Results/Limitations; describe dev_test results for the final variant as non-independent. |
| 3.2 | MAJOR | **Wilcoxon signed-rank tests are dominated by clinically irrelevant tiny differences.** In AF-free patients PA-HMMQ returns small non-zero burdens (posterior probabilities never exactly 0) while counting returns exactly 0, producing many tiny non-zero paired differences of the "wrong" sign. The rank test therefore partly tests *exact-zero reporting*, not clinically relevant accuracy. | Table 4 (rank-biserial r > 0 vs CC-MF, ACC, PACC, EMQ despite negative mean differences) | Keep the pre-specified test unchanged, but add a clearly labelled post-hoc sensitivity analysis with burden estimates reported at a clinical resolution of 0.1 percentage point, and interpret effect sizes primarily via mean paired differences with CIs. |
| 3.3 | MODERATE | **Multiplicity beyond the primary family.** Many families of tests (3 detectors × 2–3 targets × 5 cohorts). Only the primary family is confirmatory. | Table S14 | State that only LightGBM / pooled external / final-vs-8 is confirmatory; others exploratory without cross-family correction. |
| 3.4 | MODERATE | **Bootstrap CIs ignore model (seed) variability**, and Clopper–Pearson intervals for coverage are computed from seed-averaged coverage. | Methods | State these approximations; seed SDs are reported separately. |
| 3.5 | MODERATE | **Selection optimism in R1:** emission selection on calA where the source dynamics are also fitted. | S1 §7 | Note in Methods/S1. |
| 3.6 | MINOR | Development test sets are small (≈49 patients per seed) — large SDs (≈1 pp). | Table 2 | Note. |
| 3.7 | MINOR | Baseline fairness verified: all estimators share the same detector outputs, the same calibration patients (calA) and no estimator was tuned on test/external data; thresholds fixed at 0.5. | code review (`run_main.py`, `burden.py`) | None (state in Methods). |

Recommendation: major revision.

---
# Author response and actions (round 3)

| # | Action | Status |
|---|---|---|
| 3.1 | Methods (partitioning), Results (primary analysis) and Limitations now state that dev_test results of the final variant are not independent of its selection; external cohorts are the only clean test. | Fixed |
| 3.2 | New post-hoc analysis (`analyze.py`: estimates rounded to 0.1 pp before testing → `table17_rounded_tests`, `statistics.json: tests[...|rounded0.1pp]`); Results report it; Methods state that mean differences are the primary effect size for interpretation. | Fixed (new analysis) |
| 3.3 | Methods: confirmatory vs exploratory families defined. | Fixed |
| 3.4 | Methods: approximations stated. | Fixed |
| 3.5 | Methods/S1: R1 selection optimism stated. | Fixed |
| 3.6 | Limitations: small development test sets. | Fixed |
| 3.7 | Methods sentence on shared calibration and fixed thresholds. | Fixed |
