# Review round 9 — Associate Editor, EP Europace (fit, evidence, completeness, reviewer risk)

**Question asked: would this manuscript survive peer review at EP Europace?**

## Assessment
* **Scope/fit.** AI-based AF-burden estimation from ambulatory ECG with external validation in three countries is within scope (digital health, arrhythmia diagnostics) and the journal recently published smartwatch AF-burden work. However, the readership is clinical; the manuscript's centre of gravity (estimator comparison, conformal prediction) is methodological. Clinical reviewers will ask "what changes for my patients?" — the clearest answer is the specificity gain for AF presence and the trade-off of missed short AF.
* **Novelty.** After rounds 2 and 8 the paper is honest that the HMM is not new and that a tuned median filter captures most of the accuracy gain. What remains novel: systematic, pre-registered comparison of burden-aggregation strategies across three detectors and three external cohorts; negative findings on prevalence correction; conformal burden intervals with external coverage and local-recalibration analysis. This is a *moderate* novelty level for a Q1 clinical journal: acceptable as an evaluation study, but a reviewer may judge the method contribution incremental.
* **Evidence.** Five seeds, patient-level splits, external cohorts untouched, leakage audit, robustness, sensitivity analyses — strong. Weakness: the pre-registered specification failed and the final variant was chosen post hoc on development data; this is disclosed thoroughly.
* **Completeness/reproducibility.** Code, configuration, per-patient results, automated table/figure/number generation; EHRA AI checklist; TRIPOD+AI stated. Good. Missing: public repository URL (placeholder) and author information (placeholders).
* **Guideline compliance.** Structure, word count, abstract headings, What's New, references, alt text, declarations — compliant (round 7). Graphical abstract "particularly encouraged": not yet provided.

## Remaining concerns to fix before submission
| # | Severity | Concern | Action |
|---|---|---|---|
| 9.1 | MAJOR | No **graphical abstract** (strongly encouraged for Clinical Research articles; landscape, separate file). | Generate from result data (key estimates + intervals) as `graphical_abstract.tiff/png`. |
| 9.2 | MAJOR | Clinical message must be visible in the first lines of the Discussion and in the Conclusion: (i) fewer spurious AF diagnoses, (ii) a few short AF episodes missed, (iii) interval coverage not guaranteed under shift → local recalibration needed. | Check wording (present after rounds 1, 5, 8). |
| 9.3 | MODERATE | Title is technical for a clinical journal. Consider: "Temporal modelling of atrial fibrillation burden from ambulatory ECG with uncertainty intervals: multinational external validation". | Keep current title (accurate; no abbreviations) but ensure the running title is clinical. Decision: retain; authors may adapt. |
| 9.4 | MODERATE | Author/affiliation/funding/COI placeholders and repository URL must be completed by the authors. | Flag in cover letter/risk report. |
| 9.5 | MINOR | Supplementary material is extensive (19 tables, 8 figures) — acceptable (no limit), but ensure every supplementary item is cited in the main text. | Check in final audit. |

## Editor's decision (simulated)
Likely outcome after external review: **major revision** (risk of rejection on novelty grounds by a methodological reviewer is real but reduced by the honest framing and the clinical specificity analysis).

---
# Author response (round 9)
* 9.1 — Graphical abstract generated from result files (`src/visualization/figures.py: fig_graphical_abstract` → `figures/graphical_abstract.tiff/.png`, landscape, 300 dpi); shows per-cohort error, AF-presence specificity/sensitivity and per-cohort interval coverage (including the Japanese under-coverage). Copied to the manuscript folder as a separate upload file.
* 9.2 — First paragraph of the Discussion and the Conclusion contain the three clinical messages (checked).
* 9.3 — Title retained (accurate, no abbreviations); authors may simplify.
* 9.4 — Placeholders listed in the rejection-risk report and cover letter.
* 9.5 — Final audit checks that every supplementary table/figure is cited.
