# S1 — Research design, topic selection and pre-specified analysis plan

*Written and committed BEFORE any model was trained or any result inspected (git history is the timestamp).*

## 1. Candidate research directions considered (Phase 1)
Constraint set: fit to EP Europace (arrhythmia/EP, clinical relevance, AI checklist), publicly available data, CPU-only compute (4 cores, 15 GB RAM, no GPU), reproducible within one session.

| # | Direction | Main reason accepted / rejected |
|---|---|---|
| 1 | AF-burden estimation as a per-patient quantification problem with calibrated uncertainty, multinational external validation (RR intervals) | **Selected** (see §2) |
| 2 | Selective (abstaining) single-lead ECG AF detection on CinC 2017 | Rejected: close to Elul et al. PNAS 2021 (uncertainty/reject option on CinC2017) and 2026 conformal AI-ECG papers |
| 3 | PPG-based AF detection generalisation | Rejected: public PPG-AF data too small / fragmented |
| 4 | AF prediction from sinus-rhythm 12-lead ECG | Rejected: requires large longitudinal cohorts not public |
| 5 | QTc estimation with deep learning | Rejected: QTcNet (Europace) exists; reference labels not public at scale |
| 6 | PVC-burden quantification from Holter | Rejected: inter-patient beat classification heavily studied; ventricular morphology needs raw ECG + GPU |
| 7 | Ventricular arrhythmia detection for wearable defibrillators | Rejected: very small public datasets (CUDB/VFDB), saturated literature |
| 8 | Brugada ECG detection | Rejected: single small public cohort, no external validation possible |
| 9 | Federated AF detection across hospitals | Rejected: artificial federation on public data; weak clinical relevance |
| 10 | AF onset prediction minutes ahead (PAF prediction) | Rejected: tiny datasets (AFPDB), unclear clinical value |
| 11 | Atrial flutter vs AF discrimination from RR | Rejected: too few AFL episodes publicly |
| 12 | Benchmark of RR-based AF detectors across public DBs | Rejected as stand-alone (incremental vs ArNet2/Haekal 2026); kept as the evaluation backbone of #1 |
| 13 | Signal-quality-aware AF detection on raw ECG | Rejected: raw-signal DL needs GPU for multinational scale |
| 14 | Monitoring-duration-dependent false-positive AF diagnosis control | Partially merged into #1 (patient-level AF-free false burden is a pre-specified endpoint) |
| 15 | Sleep-apnoea / AF interplay from Holter | Rejected: no jointly annotated public data |
| 16 | Conformal intervals for wearable heart-rate during AF | Rejected: reference data unavailable |

## 2. Stress test of the selected direction (editor perspective)
* *Incremental?* RR-based AF detection is mature (ArNet/ArNet2, TAF-Tracker, many feature/GBM methods). The contribution is therefore **not** a new detector but a statistically principled *burden layer* (quantification + uncertainty) that is detector-agnostic. Risk: reviewers may still see it as post-processing → mitigated by showing it on three detectors and by clinically interpretable endpoints.
* *Already solved?* Haekal et al. (Physiol Meas 2026) show that probability-averaged burden is biased under dataset shift and fix it by **labelled** target recalibration; Hennings et al. 2023 show commercial AI agreement in one cohort; no work found applying label-shift quantification or distribution-free per-patient intervals to AF burden (PubMed/arXiv searches 2026-11-10: 0 hits for AF burden + quantification/label shift/prior shift; 0 for AF burden + conformal).
* *Simpler method suffices?* Explicitly tested: classify-and-count, median filtering, isotonic recalibration, ACC/PACC/EMQ and a non-adaptive HMM are all baselines. A null result is possible and will be reported.
* *Dataset too small / leakage?* ~240 development patients (6 PhysioNet DBs) + 3 external multinational cohorts (Japan SHDB-AF 98 annotated patients; China CPSC2021 105 patients; Canada Icentia11k random 800-patient subset). All splits at patient level.
* *Depth for a full article?* Main comparison, ablations, robustness to R-peak errors and ectopy, external validation, sensitivity analyses, efficiency, error analysis → sufficient.

## 3. Novelty map (Phase 4)
| Existing work | Contribution | What it does not address |
|---|---|---|
| Chocron et al. 2021 (ArNet, IEEE TBME) | RNN on RR for AF burden; external test | No bias correction for patient prevalence; no per-patient uncertainty |
| Biton et al. 2023 (ArNet2, npj Digit Med) | Generalisation of RR DL across geography/age/sex; AFB error secondary | Point estimates only; AFL failure mode noted |
| Haekal et al. 2026 (Physiol Meas) | Calibration-aware probability burden; external recalibration (Platt/isotonic) with **target labels** | Label-free correction; uncertainty intervals; temporal structure |
| Karimizadeh et al. 2026 (Heart Rhythm O2) | RR feature ML burden on textile ECG (MAE 1.3%) | Uncertainty; quantification bias |
| Hennings et al. 2023 (CVDHJ) | Commercial AI vs manual burden (Swiss-AF) | Method transparency; uncertainty |
| Abbasi et al. 2026 (Heart Rhythm) / El Allam 2026 (Physiol Meas) | Conformal coverage under shift for 12-lead classification | Burden (a continuous per-patient quantity); long-term monitoring |
| Forman 2008; Saerens 2002; Bella 2010 (quantification learning) | ACC/EMQ/PACC prevalence estimators for i.i.d. samples | Temporal dependence; per-patient application in rhythm monitoring |
| **Proposed** | Burden as per-patient prevalence: (i) **patient-adaptive HMM quantification (PA-HMMQ)** – fixed, source-calibrated emissions + per-patient MAP-EM rhythm dynamics; (ii) **posterior-normalised split-conformal burden intervals**; (iii) clinically framed multinational external evaluation | — |

## 4. Hypotheses and research questions (Phase 5)
**Primary hypothesis H1.** For a fixed window-level detector, PA-HMMQ yields lower per-patient absolute burden error than classify-and-count (CC) on pooled external patients.

* **RQ1 (main, Exp 1/2):** Does PA-HMMQ reduce per-patient burden error vs CC, PCC, PCC-iso, CC-MF, ACC, PACC, EMQ, HMM-src, consistently across three detectors?
* **RQ2 (ablation, Exp 3):** Which components matter — calibrated emissions vs raw scores, temporal model, patient-level adaptation, prior strength κ?
* **RQ3 (uncertainty, Exp 1/5):** Do posterior-normalised conformal intervals attain nominal 90% coverage in held-out development patients, and how does coverage degrade under external shift? Are they narrower than constant-width conformal at equal coverage?
* **RQ4 (robustness/generalisation, Exp 4/5):** How do estimators behave under simulated missed/false R-peaks, timing jitter, ectopy, reduced training data, and across Japan/China/Canada cohorts and AF-free patients?
* **RQ5 (cost/clinical impact, Exp 6/8):** What is the computational overhead per 24-h recording, and what are the residual failure modes (AFL, ectopy, low burden)?

## 5. Pre-specified protocol
* **Data.** Development: LTAFDB, AFDB, MITDB, NSRDB, NSR2DB, BIDMC-CHF (US). External: SHDB-AF v1.0.1 (Japan), CPSC2021 (China), Icentia11k (Canada; 800 patients sampled uniformly at random with seed 20261110, first 10 segments each, sampled without looking at labels). Beat annotations from the databases (manual or database-provided automatic R peaks); rhythm reference = database rhythm annotations.
* **Units.** 60-beat non-overlapping windows of valid RR (0.2–3.0 s). Window label AF if ≥50% of its time is AF. **Reference burden** = time in AF / analysed time per patient (AFL counted as non-AF; sensitivity analysis with AF+AFL).
* **Splits.** Per seed, development patients split (stratified by database × AF presence) into train 45% / calA 15% / calB 20% / test 20%; 15% of train patients as inner validation for early stopping. calA → all source calibration (threshold statistics, isotonic map, emission histograms, source HMM dynamics). calB → conformal calibration only. External cohorts are never used for training, calibration or tuning.
* **Seeds (fixed a priori):** 11, 22, 33, 44, 55. All results reported as mean ± SD over seeds; no seed selection.
* **Fixed hyper-parameters (chosen a priori, not tuned on test/external data):** threshold 0.5; κ = 10; 50 histogram bins on logit ∈ [−14, 14]; α = 0.10; ε = 0.002; 200 FFBS samples; RRNet 12 epochs max, patience 3, AdamW lr 1e-3; LightGBM 400 trees max, early stopping 50 on inner validation.
* **Primary endpoint.** Per-patient absolute burden error (percentage points) on the pooled external cohorts (all three), averaged over seeds, with detector = LightGBM pre-specified as the primary detector (RRNet and Classical-LR as secondary).
* **Primary test.** Two-sided Wilcoxon signed-rank test on per-patient (seed-averaged) absolute errors, PA-HMMQ vs each comparator; Holm correction over the 8 comparators; effect size = median paired difference with patient-level bootstrap 95% CI (2000 resamples) and matched-pairs rank-biserial correlation. Secondary: per-cohort tests, Bland–Altman bias/LoA, Lin's CCC, threshold sensitivity/specificity (≥30 s AF, ≥1%, ≥10%) with McNemar tests, conformal coverage with Clopper–Pearson 95% CI.
* **Experiments.** Exp1 main; Exp2 baselines (3 detectors × 9 estimators); Exp3 ablation (raw-score emissions, no temporal model = EMQ, fixed dynamics = HMM-src, κ ∈ {0,1,3,10,30,100}); Exp4 robustness (missed beats 2/5%, false beats 2/5%, jitter 10/25 ms, simulated premature beats 5/10% on SHDB-AF; training-data fraction 25/50/100%); Exp5 generalisation (per external cohort, AF-free vs AF patients, AF+AFL definition, sex/age subgroups in SHDB-AF where metadata permit); Exp6 efficiency (parameters, runtime per 24-h recording); Exp7 sensitivity (κ, bins, α, ε, window length 30/120 beats for LightGBM); Exp8 error analysis (largest errors, association of error with ectopy, AFL and burden level).

## 6. Amendment A1 (recorded 2026-11-10, after the one-seed *quick* pipeline check, before the full 5-seed run)
The quick check (1 seed, 100 trees, 40-patient external subsets) suggested that the ablation
"PA-HMMQ[rawE]" (emission likelihoods taken directly from the detector probability, (1−p, p), instead
of calibration-set class-conditional histograms) may outperform the pre-specified calibrated emission model.
Development-only diagnosis (calB patients): the calibrated emissions are flatter (label noise at window level
bounds the empirical likelihood ratio), so the sticky source rhythm dynamics dominate and short non-AF
stretches inside AF are over-smoothed (e.g., MITDB 219).
**Decision rule fixed now:** the emission model of the final PA-HMMQ will be chosen *using development
held-out patients only* (calB ∪ dev_test, pooled over the 5 seeds, primary detector LightGBM, mean per-patient
absolute error). External cohorts play no role in this choice. Both variants will be reported in the
manuscript (main tables + ablation), and the choice will be described as a post-hoc, development-data-driven
modification. The pre-registered variant remains in all tables.

## 7. Revision R1 (post hoc; recorded 2026-11-11 after inspecting seed-11/22 results, before the full 5-seed analysis)
**Observation (development data).** (i) The best emission model differs by detector: on development held-out
patients (calB ∪ dev_test) probability emissions were better for LightGBM and Classical-LR, but calibrated-histogram
emissions were better for RRNet (A1 had been decided on LightGBM only). (ii) Per-patient adaptation of the dynamics
(PA-HMMQ vs HMM-src with the same emissions) changed errors by ≤0.2 pp in either direction, and errors were flat over κ.
**Hypothesis.** Burden error depends mainly on the *sharpness* of the emission likelihood ratio relative to the detector's
actual reliability; this sharpness can be calibrated per detector on labelled calibration patients.
**Change.** Emission model selected per seed and detector on calibration-A patients only, by the mean per-patient
burden error of the fixed-dynamics HMM, among {calibrated histogram; probability emissions with likelihood ratio
(p/(1−p))^(1/T), T ∈ {0.5, 1, 2, 4, 8}}. Estimators "HMM-src[sel]" and "PA-HMMQ[sel]" (+ normalised conformal interval,
quantile on calB) are added. calB, development test and external cohorts are not used for the selection.
**Reporting.** R1 is reported as a post-hoc analysis. The pre-registered PA-HMMQ and the A1 variant remain in all tables,
the ablation states explicitly that patient adaptation did not contribute, and the primary pre-specified test is
reported unchanged. The fixed-dynamics HMM with the same emission is added as the fair comparator for every PA-HMMQ variant.

**Disclosure added after review round 1.** The one-seed quick check that preceded Amendment A1 also printed burden
errors for 40-patient subsets of SHDB-AF and CPSC2021 (and the A1 variant had lower error there). The A1 decision rule
itself was evaluated only on development patients (calB ∪ dev_test, five seeds), and the full external analysis was run
afterwards; nevertheless, knowledge of these subset results may have influenced the decision to formalise A1.
