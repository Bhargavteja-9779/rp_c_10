# Review round 1 — Reviewer #1 (general methodological and clinical review, EP Europace)

Manuscript version reviewed: v1 (build of 2026-11-11 ~07:50 UTC; full 5-seed main results; R1 partially available; robustness pending).
Stance: hostile but fair; praise omitted.

## Summary of the submission
A burden layer (two-state HMM over 60-beat RR windows, optionally patient-adaptive) is placed on top of three AF detectors; nine estimators are compared in 243 development and 988 external patients; split-conformal intervals are added.

## Issues

| # | Severity | Issue | Evidence | Required fix |
|---|---|---|---|---|
| 1.1 | MAJOR | **Forking paths around the final method.** The pre-registered specification failed; the "final" emission model was fixed by Amendment A1 *after* a one-seed quick check. The quick check also printed errors for 40-patient subsets of two external cohorts. Even though the A1 rule uses development data only, the authors had seen external numbers when they wrote the rule. This is not disclosed. | S1 §6; experiment history | Disclose explicitly in Methods, Limitations and S1 that quick-check external subset results had been displayed; state that the A1 rule was evaluated on development data only and that full external results were computed afterwards. |
| 1.2 | MAJOR | **Novelty of the effective method.** The benefit comes from an HMM with fixed source dynamics and probability emissions. Markov modelling of RR intervals for AF detection is decades old (the AFDB itself was created for a Markov-model RR detector). The Introduction implies the temporal approach is new. | Results "What drives the gain"; Introduction | Cite the earlier Markov-model RR approach; reposition the contribution as (i) a systematic comparison of burden-aggregation strategies incl. quantification estimators, (ii) the finding that temporal modelling, not prevalence correction, matters, and (iii) conformal burden intervals with external coverage assessment. |
| 1.3 | MAJOR | **Sensitivity loss for AF presence is under-described.** Specificity improves 0.74→0.91 but sensitivity falls 0.99→0.94. The abstract presents this as a mere "cost". Which patients are missed, and how much AF do they have? Missing ≥6 min of AF may matter clinically (subclinical-AF thresholds). | Table S7; Results "Patient classification" | Add a machine-generated analysis of patients newly missed vs counting (n, AF minutes); discuss clinical implications, incl. the ≥6-min threshold. |
| 1.4 | MAJOR | **Claim "calibrated intervals" in the Conclusion is too strong.** Coverage was 0.84 in SHDB-AF. | Table 5 | Weaken to "near-nominal coverage in two of three external cohorts". |
| 1.5 | MAJOR | **Effect size and clinical relevance.** A mean reduction of 0.47 pp with zero median difference is small. The pooled endpoint is dominated by Icentia11k (790/988 patients, mostly AF-free). | Table 2, Table 4 | State the pooled endpoint's composition; report per-cohort effects prominently (already in Table 2); frame clinical relevance through threshold classification rather than MAE. |
| 1.6 | MODERATE | Licences described as "open licences": Icentia11k is CC BY-NC-SA 4.0 (non-commercial), CPSC2021 CC BY 4.0, others ODC-By. | downloaded LICENSE files | State exact licences in Table S1 and Ethics. |
| 1.7 | MODERATE | P-value formatting "P = <0.001". | Results | Fix token formatting. |
| 1.8 | MODERATE | Efficiency numbers were measured while other experiments were running (CPU contention) — e.g. RR-feature extraction 797 ms/24 h and RRNet inference are inflated. | efficiency.json timestamp | Re-measure on an idle machine; state hardware. |
| 1.9 | MODERATE | Abstract is long (~330 words). | Abstract | Shorten to ≈250–280 words. |
| 1.10 | MODERATE | Statements about robustness ("ranking largely preserved") and R1 ("did not improve") are written before the corresponding experiments finished. | Results | Re-verify against final outputs (claim audit) and rewrite as needed. |
| 1.11 | MINOR | Subscripts lost in the plain-text export (e.g. "dij"). | Final_Manuscript.md | Check DOCX rendering (subscripts are real runs there). |
| 1.12 | MINOR | "≥30 s of AF" presence is evaluated on analysed time only; recordings differ in length (CPSC2021 records are short). | Methods | Note in Methods/Limitations. |

## Recommendation
Major revision.

---
# Author response and actions (round 1)

| # | Action taken | Status |
|---|---|---|
| 1.1 | Disclosure added to Methods (Burden estimators), Limitations and S1 §6: the quick check displayed results for 40-patient subsets of SHDB-AF and CPSC2021; the A1 rule used development patients only. | Fixed (text) |
| 1.2 | Verified the Moody & Mark 1983 Markov-model RR AF detector reference (PhysioNet AFDB citation) and added it; Introduction and Discussion reworded: temporal modelling is not new per se; the contribution is the burden-specific comparison, the negative result for prevalence correction and adaptation, and conformal burden intervals. | Fixed (text + reference) |
| 1.3 | New machine-generated analysis (`analyze.py` → `table16_newly_missed`, `statistics.json: newly_missed`) and Results/Discussion text on missed patients incl. the ≥6-min threshold. | Fixed (new analysis) |
| 1.4 | Conclusion and Abstract reworded. | Fixed |
| 1.5 | Pooled composition stated in Methods; per-cohort results emphasised; clinical relevance framed by threshold classification. | Fixed |
| 1.6 | Table S1 licence column corrected from the downloaded LICENSE files; Ethics statement updated. | Fixed |
| 1.7 | New P-value token prints "P < 0.001"/"P = 0.229". | Fixed |
| 1.8 | Efficiency re-run scheduled after all experiments finish, on an otherwise idle machine. | Fixed in final build (see final_audit.md) |
| 1.9 | Abstract shortened. | Fixed |
| 1.10 | Robustness/R1 sentences rewritten from final outputs in round 3 claim audit. | Deferred to after experiments → done in later round |
| 1.11 | Verified in DOCX render (subscript runs). | Checked |
| 1.12 | Sentence added to Limitations. | Fixed |
