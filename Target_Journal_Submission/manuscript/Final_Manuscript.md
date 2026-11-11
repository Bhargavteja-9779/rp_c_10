# Temporal quantification of atrial fibrillation burden with distribution-free uncertainty intervals: development and multinational external validation


## Abstract

Background and Aims Automated tools estimate atrial fibrillation (AF) burden by counting windows classified as AF—a biased estimator of a proportion—without uncertainty. We developed and externally validated a detector-agnostic burden estimator with per-patient uncertainty intervals.

Methods A hidden Markov burden layer (PA-HMMQ) converts the output of any beat-to-beat interval AF detector into burden, modelling the persistence of rhythm and optionally re-estimating each patient's rhythm dynamics; split-conformal calibration gives 90% intervals. Three detectors were developed in 243 patients (USA) and evaluated without recalibration in 988 patients from Japan, China and Canada. The pre-registered primary endpoint was the per-patient absolute burden error in pooled external cohorts.

Results The pre-registered specification did not outperform classify-and-count (3.07 ± 0.30 vs 2.99 ± 0.26 percentage points [pp]). With emissions selected on development data before the full analysis, the error was 2.52 ± 0.24 pp (paired difference -0.47 pp, 95% CI -0.56 to -0.38), lower on average than all eight comparators and with all three detectors, although rank tests were not significant against three comparators. Temporal modelling, not per-patient re-estimation of dynamics, explained the gain, and a tuned median filter recovered most of it. Specificity for AF presence (≥30 s) rose from 0.74 to 0.91 while sensitivity fell from 0.99 to 0.94. Conformal intervals covered 0.95 of external patients (target 0.90) but 0.84 in the Japanese cohort. Atrial flutter caused the largest errors.

Conclusion Modelling rhythm persistence when aggregating detector outputs modestly reduced burden error and spurious AF across three continents, and conformal intervals achieved near-nominal coverage in two of three external cohorts. Flutter remains the main limitation of RR-based burden estimation.

Keywords Atrial fibrillation burden • Ambulatory electrocardiography • Artificial intelligence • Uncertainty quantification • Conformal prediction • External validation


## What's New?

- In 988 external patients from Japan, China and Canada, a hidden Markov burden layer placed on top of RR-interval AF detectors reduced the mean absolute AF-burden error from 2.99 to 2.52 percentage points compared with counting AF-classified windows, consistently across three detectors.
- The benefit came from modelling the temporal persistence of rhythm—a tuned median filter captured most of it—whereas classical prevalence-correction methods and per-patient re-estimation of rhythm dynamics did not help, and recalibrating window probabilities on the development population worsened burden estimates.
- False AF diagnoses in AF-free patients fell (specificity 0.74 to 0.91), with a reduction in sensitivity.
- Conformal intervals reached nominal 90% coverage of individual patients' burden in two of three external cohorts but under-covered in the third; atrial flutter remained the dominant source of error.

## Introduction

Atrial fibrillation (AF) is increasingly characterised by how much of the time a patient spends in the arrhythmia rather than by its mere presence. AF burden—the proportion of monitored time in AF—is associated with ischaemic stroke and other outcomes, is an endpoint of rhythm-control trials, and has become central to the interpretation of device-detected subclinical AF ^1–5. The 2024 European Society of Cardiology guidelines acknowledge burden as a clinically relevant descriptor while noting that its measurement is method-dependent ^6. With the spread of long-term Holter, patch, wearable and implantable monitoring, burden is now almost always computed automatically.

In published research pipelines, automated burden is usually obtained by running a window-level AF detector over the recording and counting (or averaging the probabilities of) the windows classified as AF ^7–10; the aggregation used by proprietary clinical software is generally undocumented. Beat-to-beat (RR) interval detectors range from classical irregularity statistics ^11–14 and feature-based machine learning ^9,15 to deep recurrent networks evaluated across geographies ^7,8,16,17. These studies report excellent window-level discrimination, but burden is a patient-level proportion, and counting classified windows is a biased estimator of a proportion whenever sensitivity and specificity are imperfect: false-positive windows inflate burden in patients with little AF, false negatives deflate it in patients with persistent AF, and the size of both errors changes with the patient's own AF prevalence ^18. Recent work has shown that burden derived from averaged detector probabilities degrades under external dataset shift unless probabilities are recalibrated with labelled data from the target cohort ^10. In addition, current tools report burden as a single number without an uncertainty statement, although a clinician deciding whether a low burden is real needs to know how wrong the estimate could plausibly be.

The machine-learning field of quantification addresses exactly the problem of estimating class proportions in a new sample whose prevalence differs from that of the training data ^18–22, and conformal prediction provides distribution-free uncertainty intervals with finite-sample coverage guarantees ^23–25. Neither has, to our knowledge, been applied to AF burden: conformal methods in electrocardiography have so far targeted diagnostic classification ^26,27, and quantification estimators assume independent samples, whereas rhythm windows are strongly dependent in time—a property exploited by Markov-model and hidden Markov model RR detectors since the earliest automated AF detection work ^28,29, but not, to our knowledge, examined systematically as a burden-estimation problem.

We therefore treated AF-burden estimation as a per-patient quantification problem and developed a detector-agnostic burden layer—a hidden Markov model quantifier that models the temporal persistence of rhythm and can re-estimate each patient's rhythm dynamics (patient-adaptive hidden Markov quantifier, PA-HMMQ)—with distribution-free conformal burden intervals. We hypothesised that correcting for each patient's own AF prevalence would reduce burden error. Following a pre-registered plan, we tested in external cohorts from Japan, China and Canada (i) whether it reduces per-patient burden error compared with classify-and-count and established quantification and smoothing methods, (ii) which of its components are responsible, (iii) whether its intervals attain nominal coverage, and (iv) how robust it is to R-peak errors, ectopy and reduced training data.


## Methods


### Study design and reporting

This was a retrospective development and multinational external-validation study using publicly available, de-identified ambulatory electrocardiogram (ECG) databases. Reporting follows TRIPOD+AI ^30 and the 2025 EHRA/HRS/ESC e-Cardiology scientific statement on artificial intelligence in clinical electrophysiology ^31; the EHRA AI checklist is provided as Supplementary material. The analysis plan, including hyper-parameters, random seeds, endpoints and statistical tests, was written and version-controlled before any model was trained (Supplementary material S1).


### Data sources

The development pool comprised six PhysioNet databases recorded in the USA ^32: the Long-Term AF Database (LTAFDB) ^33, the MIT-BIH AF Database (AFDB) ^28, the MIT-BIH Arrhythmia Database (MITDB) ^34, the BIDMC Congestive Heart Failure Database (CHFDB) ^35, and the MIT-BIH Normal Sinus Rhythm databases (NSRDB, NSR2DB). External validation used three cohorts that were never used for training, calibration or tuning: SHDB-AF, 24-h two-channel Holter recordings of Japanese patients with paroxysmal AF annotated beat-by-beat by a cardiologist ^36; CPSC2021, dynamic Holter recordings from the 4th China Physiological Signal Challenge ^37; and Icentia11k, single-lead patch recordings from Canadian outpatients with technologist-reviewed beat and rhythm labels ^38,39, from which 800 patients were sampled uniformly at random (fixed seed, without inspecting labels) and their first ten 70-min segments used. Only beat and rhythm annotation files were used (Supplementary Table S1 lists versions, licences and exclusions).


### Reference standard and units of analysis

RR intervals were derived from the database beat annotations (automatic R-peak annotations for AFDB and SHDB-AF, reviewed annotations elsewhere); intervals outside 0.2–3.0 s or outside labelled rhythm segments were excluded. Each RR interval inherited the reference rhythm at its terminating beat. RR series were cut into non-overlapping windows of 60 consecutive valid intervals. A window was labelled AF if ≥50% of its duration was annotated AF. The reference AF burden of a patient was the AF-annotated time divided by the analysed time (the total duration of complete windows; trailing runs of fewer than 60 valid intervals were excluded from both reference and estimates); atrial flutter was counted as non-AF (sensitivity analysis: AF+flutter). Recordings of the same patient were aggregated, so the unit of analysis was the patient.


### Window-level detectors

Because the proposed method operates on any detector's output, three detectors spanning model complexity were trained: (i) Classical-LR, a logistic regression on three classical irregularity features (normalised RMSSD, Shannon entropy, turning-point ratio) ^12; (ii) LightGBM, gradient-boosted trees on 16 RR features including sample-entropy-based irregularity (pre-specified primary detector); and (iii) RRNet, a convolutional–bidirectional recurrent network on the normalised RR sequence, re-implemented in the spirit of ArNet/ArNet2 ^7,8 (architecture in Supplementary material). Each detector outputs a window probability p.


### Burden estimators

For patient i with windows j of duration dij the following estimators were compared, all calibrated on held-out development patients only: classify-and-count (CC, threshold 0.5); CC after a three-window median filter (CC-MF); probabilistic CC (PCC, mean probability) ^20 and PCC after source isotonic recalibration (PCC-iso, the label-free analogue of probability recalibration ^10); adjusted CC (ACC), which corrects CC for the source true- and false-positive rates ^18; probabilistic ACC (PACC) ^20; expectation–maximisation prior adjustment (EMQ) ^19; and a two-state hidden Markov model with fixed source rhythm dynamics (HMM-src) ^40.

Proposed estimator (PA-HMMQ). Each patient's window sequence is modelled as a two-state (non-AF/AF) hidden Markov chain. Emission likelihoods are a function of the detector output only and are held fixed (label-shift assumption: the appearance of an AF window does not depend on how much AF the patient has). The rhythm dynamics—initial distribution πi and transition matrix Ai—are re-estimated for every patient by maximum-a-posteriori expectation–maximisation with a Dirichlet prior centred on the source dynamics Asrc estimated on calibration patients:

Ai(k,l) ∝ Σt ξit(k,l) + κ Asrc(k,l),

where ξ are the posterior expected transitions and κ (pre-specified 10) the prior strength. Burden is the duration-weighted posterior probability of AF, B̂i = Σj dij γij / Σj dij, γij = P(AFij | all windows of patient i). This generalises EMQ (κ→0, no temporal dependence) and HMM-src (κ→∞). The pre-registered version used emission likelihoods estimated as class-conditional histograms of logit(p) on calibration patients; a variant using the detector probability directly as likelihood (e(AF) ∝ p, e(non-AF) ∝ 1−p) was pre-specified as an ablation. Following a decision rule recorded after a one-seed pipeline check and before the full analysis, and evaluated on development patients only (Supplementary S1, Amendment A1; the pipeline check had also displayed errors for 40-patient subsets of two external cohorts), the variant with the lower development error was designated the final method; both are reported throughout. To isolate the contribution of per-patient adaptation, every PA-HMMQ variant was also compared with the HMM using identical emissions but fixed source dynamics (post hoc). A further post-hoc revision (R1) selected the emission sharpness separately for each detector on calibration patients (likelihood ratio (p/(1−p))^1/T, T ∈ {0.5, 1, 2, 4, 8}, or the histogram model).

Conformal burden intervals. Posterior burden samples were drawn by forward-filtering backward-sampling (200 samples) ^41, giving a model-based standard deviation σ̂i. On a separate set of calibration patients, nonconformity scores r = |B − B̂|/(σ̂ + ε) (ε = 0.002) were computed, and the ⌈(n+1)(1−α)⌉-th smallest score q̂ defined the interval B̂i ± q̂(σ̂i + ε), clipped to [0,1], with α = 0.10. Under exchangeability of patients, this guarantees ≥90% marginal coverage ^23,24; normalising the score by the model-based posterior standard deviation makes interval width adapt to each patient's rhythm pattern. Constant-width conformal intervals around CC, PCC-iso and PA-HMMQ, and the uncalibrated posterior credible interval, served as comparators.


### Data partitioning and leakage control

For each of five pre-specified seeds, development patients were split, stratified by database and AF presence, into training (45%; 15% of these for early stopping), calibration A (15%; all source calibration quantities), calibration B (20%; conformal quantile only) and test (20%) sets. No patient appeared in more than one set. All estimators used the same detector outputs and the same calibration-A patients, thresholds were fixed at 0.5, and no estimator was tuned on test or external data. Because Amendment A1 used calibration-B and development test patients to choose the final emission model, development test results of the final variant are not independent of its selection; the external cohorts are the only fully independent test. An automated audit fingerprinting all RR windows and recordings across all databases identified one exact duplicate recording in SHDB-AF (two files of the same subject with identical RR series), which was removed (Supplementary Table S1). Features and RR normalisation were computed within each window only.


### Endpoints and statistical analysis

The pre-specified primary endpoint was the per-patient absolute burden error (percentage points, pp) in the pooled external cohorts with the LightGBM detector; because Icentia11k contributes most pooled patients (largely AF-free), per-cohort results are reported alongside. Per-patient errors were averaged over the five seeds and compared between the proposed estimator and each comparator using two-sided Wilcoxon signed-rank tests with Holm correction across the eight comparators ^42,43; effect sizes are the mean and median paired differences with patient-level bootstrap 95% confidence intervals (2000 resamples) and matched-pairs rank-biserial correlations ^44. Secondary endpoints were Bland–Altman bias and limits of agreement ^45, Lin's concordance correlation coefficient ^46, false burden in AF-free patients, classification of patients by burden thresholds (≥30 s of AF, ≥1%, ≥10%; exact McNemar tests on seed-majority classifications), conformal coverage (Clopper–Pearson 95% CI) and interval width, and window-level discrimination and calibration of the detectors. Only the comparison of the final PA-HMMQ with the eight comparators (LightGBM, pooled external cohorts) is regarded as confirmatory; all other tests are exploratory and not corrected across families. Because many AF-free patients receive exactly zero burden from counting-type estimators but small non-zero posterior burdens from HMM estimators, rank-based tests partly reflect differences far below clinical relevance; mean paired differences with bootstrap CIs were therefore used as the primary effect size for interpretation, and a post-hoc sensitivity analysis repeated the tests with estimates reported at 0.1-percentage-point resolution. Bootstrap CIs do not include between-seed model variability (reported separately as SDs), and Clopper–Pearson intervals were computed from seed-averaged coverage. Summary statistics are mean ± standard deviation over seeds. Analyses not in the pre-registered plan (fair-comparator tests, emission selection R1, exclusion of flutter patients) are labelled post hoc. Robustness was assessed by re-analysing SHDB-AF after simulated missed R peaks (2%, 5%), false R peaks (2%, 5%), R-peak timing jitter (10, 25 ms) and premature beats with compensatory pauses (5%, 10%). Sensitivity analyses varied κ, the training-set size (25%, 50%) and the window length (30, 120 beats). Analyses used Python 3.13 with PyTorch, scikit-learn, LightGBM and SciPy; all code and the commands regenerating every number, table and figure are publicly available (Data availability).


### Ethics

Only publicly available, de-identified databases were used, under their licences (ODC-By 1.0; CPSC2021 CC BY 4.0; Icentia11k CC BY-NC-SA 4.0, non-commercial research use); the original studies obtained ethical approval and consent as described in the cited publications. No new data were collected, so additional ethical approval and consent were not required.


## Results


### Cohorts

The development pool comprised 243 patients (4,045 h of analysed RR data; 119 with AF), and the external cohorts 988 patients (8,576 h; 175 with AF and 39 with atrial flutter): SHDB-AF 93 patients (72 with AF during the recording), CPSC2021 105 patients (53 with AF) and Icentia11k 790 patients (50 with AF) (Table 1; Supplementary Figure S1). Ten of the 800 sampled Icentia11k patients had no analysable labelled windows.


### Window-level detection

All detectors discriminated AF windows well (Supplementary Table S2, Supplementary Figures S2–S4). For LightGBM, the area under the receiver operating characteristic curve was 0.992 ± 0.005 in the development test set and 0.969 ± 0.003, 0.992 ± 0.001 and 0.990 ± 0.001 in SHDB-AF, CPSC2021 and Icentia11k; window sensitivity and specificity were 0.974 and 0.972 in Icentia11k.


### Primary pre-specified analysis

With the pre-registered emission model, PA-HMMQ did not reduce burden error compared with classify-and-count in the pooled external cohorts (3.07 ± 0.30 vs 2.99 ± 0.26 pp; mean paired difference 0.09 pp, 95% CI -0.07 to 0.26; Holm-adjusted P = 0.541) and was worse than median-filtered counting (2.73 ± 0.23 pp) (Table 2; Supplementary Table S14). The primary hypothesis was therefore not supported for the pre-registered specification.

By the development-data rule of Amendment A1, applied before the full analysis, probability emissions were selected (development error 2.858 vs 3.186 pp). This final PA-HMMQ had the lowest mean error of all estimators in each external cohort (Table 2, Figure 2): 4.23 ± 0.11 pp in SHDB-AF, 2.88 ± 0.39 pp in CPSC2021 and 2.27 ± 0.33 pp in Icentia11k, versus 4.51 ± 0.12, 3.85 ± 0.76 and 2.69 ± 0.35 pp for classify-and-count. In the development test set—which, unlike the external cohorts, contributed to the A1 selection—it was not better than the pre-registered variant or the fixed-dynamics HMM (3.04 ± 1.26, 2.97 ± 1.03 and 3.00 ± 1.02 pp).

In the pooled external cohorts, the mean paired difference favoured the final PA-HMMQ over every comparator, with bootstrap 95% CIs excluding zero (Table 4; Supplementary Figure S6): -0.47 pp (-0.56 to -0.38) versus classify-and-count, -0.21 pp (-0.27 to -0.17) versus median-filtered counting and -1.33 pp (-1.50 to -1.16) versus isotonic-recalibrated probability averaging. The pre-specified Wilcoxon signed-rank tests, however, were significant after Holm correction against classify-and-count (P < 0.001), PCC, PCC-iso, EMQ and HMM-src, but not against median-filtered counting (P = 0.229), ACC (P = 0.229) or PACC (P = 0.198). Most external patients were AF-free and received near-zero burden from all estimators, so median paired differences were close to zero. When estimates were reported at 0.1-pp resolution (post hoc), the final PA-HMMQ remained better than median-filtered counting (mean paired difference -0.22 pp, Holm-adjusted P < 0.001), ACC (P < 0.001) and PACC (P < 0.001) (Supplementary Table S17); the mean gain was concentrated in patients with AF (3.82 vs 4.49 pp) and in AF-free patients with false-positive windows (mean false burden 2.24 vs 2.66 pp; Table 3).

The final PA-HMMQ had a lower mean error than classify-and-count in all nine detector × external-cohort combinations. The ranking was reproduced with the other detectors (Supplementary Tables S3–S4): pooled external error 7.44 ± 0.69 vs 8.54 ± 0.56 pp (Classical-LR) and 3.45 ± 0.70 vs 3.96 ± 0.83 pp (RRNet). Bias was 1.70 pp (classify-and-count 2.00 pp) and Lin's concordance correlation 0.902 (0.900) (Table 3, Figure 3).


### What drives the gain

Re-estimating rhythm dynamics per patient did not contribute: the final PA-HMMQ and the HMM with the same emissions but fixed source dynamics had identical error (2.52 ± 0.22 pp; mean paired difference 0.00 pp, 95% CI -0.02 to 0.02), and error was insensitive to the prior strength κ (Supplementary Table S5, Supplementary Figure S5). The improvement was therefore attributable to temporal modelling with sharp emission likelihoods. Consistent with this, a longer median filter recovered most of the gain: with the filter length selected on development patients (7 windows; post hoc), median-filtered counting reached 2.63 pp in the pooled external cohorts, versus 2.52 ± 0.24 pp for the final PA-HMMQ (mean paired difference -0.11 pp, 95% CI -0.15 to -0.07; Supplementary Table S19). Classical prevalence-correction estimators that ignore temporal dependence (ACC, PACC, EMQ) did not consistently improve on classify-and-count, and recalibrating window probabilities on development patients worsened burden error (PCC-iso 3.85 ± 0.51 pp).


### Patient classification

Using the presence of ≥30 s of AF, the final PA-HMMQ increased specificity from 0.744 to 0.914 and decreased sensitivity from 0.992 to 0.941; on seed-majority classifications it corrected 140 patients misclassified by classify-and-count and misclassified 9 that it had classified correctly (exact McNemar P <0.001). The 9 patients newly classified as AF-free by the final PA-HMMQ had between 0.9 and 8.7 min of reference AF (maximum burden 3.61%); 1 of them had ≥6 min (post hoc; Supplementary Table S16). For a burden of ≥1%, specificity was 0.923 versus 0.850 and sensitivity 0.971 versus 0.992 (Supplementary Table S7).


### Uncertainty intervals

Normalised conformal intervals around the final PA-HMMQ covered the reference burden in 0.910 of development test patients and 0.949 (95% CI 0.933–0.961) of external patients (0.843 SHDB-AF, 0.949 CPSC2021, 0.961 Icentia11k); mean width 3.94 pp and median width 1.99 pp (Table 5, Figure 4). Coverage was lower in patients with AF (0.894) than in AF-free patients (0.961). Constant-width conformal intervals around classify-and-count reached similar coverage (0.926) but were much wider (mean 13.97 pp), and uncalibrated posterior credible intervals under-covered (0.834). In a post-hoc experiment, recomputing the conformal quantile from 20 randomly chosen, locally labelled patients of each external cohort restored mean coverage to 0.91 in SHDB-AF, 0.90 in CPSC2021 and 0.91 in Icentia11k, but coverage varied between draws (SHDB-AF 5th percentile 0.78), remained below nominal in patients with AF (0.88, 0.88 and 0.81), and widened SHDB-AF intervals to a mean of 17.02 pp (Supplementary Table S18).


### Post-hoc emission selection

Selecting the emission sharpness per detector on calibration patients (Revision R1, post hoc) gave a pooled external error of 2.74 ± nan pp with LightGBM, 11.07 ± nan pp with Classical-LR and [PENDING] pp with RRNet, and did not improve on the A1 specification (Supplementary Tables S5, S15).


### Robustness and sensitivity analyses

In SHDB-AF, errors of all estimators increased with simulated false R peaks and premature beats, while missed beats and timing jitter had smaller effects; the ranking of estimators was largely preserved (Figure 5; Supplementary Tables S9–S10). Reduced training data and 30- or 120-beat windows are reported in Supplementary Table S11.


### Error analysis

Errors were largest in patients with intermediate burden and in patients with atrial flutter (Figure 6; Supplementary Tables S6, S13). Of the 988 external patients, 39 had flutter; with an AF+flutter reference the error of the final PA-HMMQ was 1.64 pp, and excluding flutter patients (post hoc) 1.19 pp (classify-and-count 2.11 and 1.67 pp; Supplementary Table S8). Absolute error correlated with flutter burden (Spearman ρ = 0.298) and reference burden (ρ = 0.459), inversely with recording duration (ρ = -0.307), and only weakly with ectopic beats (supraventricular ρ = -0.030; ventricular ρ = 0.108; Supplementary Figure S7). Error did not differ materially by sex or age in SHDB-AF (Supplementary Table S12).


### Computational cost

On a 4-core CPU, the burden layer required a median of 244 ms per 24-h recording (288 ms including posterior sampling for the interval), compared with 797 ms for RR-feature extraction and 12 ms for LightGBM inference (Supplementary Figure S8).


## Discussion

In 988 patients from three continents who contributed 8,576 hours of ambulatory recordings, aggregating detector outputs with a hidden Markov burden layer reduced the mean per-patient AF-burden error compared with counting AF-classified windows and with eight alternative estimators, for three detectors of very different complexity, and markedly reduced false AF diagnoses in AF-free patients; conformal calibration produced per-patient intervals whose coverage met the 90% target in two of three external cohorts but fell short in the Japanese cohort. Equally important are the negative findings: the pre-registered specification did not outperform counting, our central hypothesis—that correcting for each patient's own AF prevalence reduces burden error—was refuted, because per-patient re-estimation of rhythm dynamics added nothing, and the absolute improvement was modest.


### Interpretation

Temporal modelling of RR intervals is not new—the MIT-BIH AF Database was created to develop a Markov-model detector ^28, and hidden Markov AF detectors were evaluated on ambulatory ECG more than two decades ago ^29—so the contribution of this study is not the hidden Markov model itself but the burden-specific comparison of aggregation strategies, the refutation of prevalence correction as the mechanism, and the conformal burden intervals. Indeed, a median filter of suitable length captured most of the accuracy gain; the practical advantage of the probabilistic model over a tuned smoother lies less in accuracy than in the posterior distribution it provides, which is what makes per-patient intervals possible. Burden is a property of a patient's rhythm trajectory: an isolated AF-like window inside long sinus rhythm, or a short regular stretch inside persistent AF, is more likely a classification error than a rhythm change. A temporal model removes much of this window-level noise, which is why median filtering and hidden Markov smoothing improved on counting. The magnitude of the gain depended on how sharply detector outputs were translated into evidence: calibration-set class-conditional histograms flattened the likelihood ratios because window labels near rhythm transitions are noisy, letting sticky source dynamics over-smooth genuine rhythm changes, whereas the detector's own probability preserved discriminating evidence. Contrary to our hypothesis, patient-specific prevalence did not need explicit correction once temporal structure was modelled—with sharp emissions the likelihood dominates the prior over rhythm dynamics, which explains the insensitivity to κ. Quantification estimators designed for independent samples (ACC, PACC, EMQ) ^18–20 did not reliably improve on counting, and recalibrating window probabilities on the development population made burden estimates worse. A probability calibrated on a development population embeds that population's AF prevalence and pulls every patient's estimate towards it; good classifier calibration is therefore not sufficient for unbiased burden estimation, which complements the observation that recalibration with labelled target data improves probability-based burden ^10.


### Clinical implications

AF burden is increasingly used to stratify risk and to evaluate therapy ^1–3, and device- or patch-derived burden informs decisions about subclinical AF ^4,5. The clinically most visible effect was the reduction of spurious AF in AF-free patients: with counting, 26% of external patients without ≥30 s of reference AF were assigned ≥30 s of AF (final PA-HMMQ 9%), which in long-term monitoring may trigger further investigation or anticoagulation discussions. This came at the cost of classifying 9 patients with 0.9–8.7 min of reference AF as AF-free, 1 of them above the 6-min threshold used for device-detected subclinical AF; this trade-off should be weighed against the purpose of monitoring, and a lower decision threshold on the posterior AF time may be preferable for screening. The burden layer requires no retraining of an existing detector, adds well under a second of computation per 24-h recording, and supplies an interval indicating whether a reported burden is distinguishable from zero or from a decision threshold. Because conformal coverage is guaranteed only for patients exchangeable with the calibration set, intervals should be recalibrated locally when a device or population differs substantially, as recently argued for AI-ECG classifiers ^26; in our data a small local calibration sample restored marginal coverage on average but not reliably, and not in patients with AF, so larger local samples or conditional calibration methods are needed. The layer operates offline on a complete recording, as is usual for Holter and patch reports, rather than in real time; its cost grows linearly with recording length, so multi-week patch recordings are feasible, whereas implantable loop recorders, which store episodic electrograms rather than continuous RR series, are outside its scope.


### Comparison with previous work

Deep RR-interval models such as ArNet and ArNet2 ^7,8 and feature-based pipelines ^9 report strong window-level performance and low burden error, and commercial AI burden agrees closely with manual assessment in selected cohorts ^47. Reported errors are not directly comparable across studies because populations, monitoring durations, reference definitions and error metrics differ (for example, a median absolute error of 1.3% in AF patients wearing textile ECG ^9). Those studies report point estimates; the present work is complementary, operating on top of any detector, comparing aggregation strategies systematically and adding patient-level uncertainty. Consistent with ArNet2, atrial flutter was the dominant failure mode of RR-based burden estimation ^8: flutter with variable conduction produces irregular RR intervals indistinguishable from AF without atrial activity information. Whether flutter time should count towards burden is partly definitional—stroke-prevention recommendations for flutter largely follow those for AF ^6—and with an AF+flutter reference the errors of all estimators fell substantially.


### Limitations

First, the pre-registered specification failed; the final emission model was chosen on development data after a one-seed check (Amendment A1) and the per-detector emission selection (R1) and flutter-exclusion analyses were post hoc, so the external results for the final method, although never used for any decision, should be regarded as requiring confirmation in further cohorts. Second, the improvement was modest (a mean of -0.47 pp versus counting), rank-based tests were not significant against three comparators, and the development test set did not favour the final over the pre-registered variant. Third, the study used retrospective public databases with heterogeneous annotation processes; reference labels, particularly in Icentia11k, may contain errors, and R peaks were taken from database annotations rather than from a uniform detector, although simulated R-peak errors were examined. Fourth, the development pool was modest (243 patients, about 49 test patients per seed) and from one country, and development test results of the final variant are not independent of its selection. Fifth, conformal coverage is marginal over patients, was lower in patients with AF, and is not guaranteed under distribution shift. Sixth, 60-beat windows limit resolution for episodes shorter than about 30–60 s, and AF presence was assessed over the analysed time only, which was short for many CPSC2021 recordings. Seventh, the cohorts differed in case mix (SHDB-AF comprised patients with known paroxysmal AF, Icentia11k largely AF-free outpatients), which affects prevalence-dependent metrics; Icentia11k was represented by a random subset of patients and segments, and the reduced-training and window-length analyses omitted it. Finally, no outcome data were available, and photoplethysmography-based wearables, which are increasingly used for burden monitoring ^48, were not studied.


## Conclusions

Accounting for the temporal persistence of rhythm when converting AF-detector outputs into burden modestly but consistently reduced burden error and substantially reduced spurious AF in AF-free patients across Japanese, Chinese and Canadian cohorts and three detectors, and conformal calibration provided per-patient burden intervals with near-nominal coverage in two of three external cohorts. Per-patient re-estimation of rhythm dynamics and classical prevalence-correction methods did not add benefit. Atrial flutter remains the main obstacle to accurate RR-based burden assessment and should be addressed before burden thresholds derived from such tools are applied clinically.


## Acknowledgements

We thank the creators and maintainers of the PhysioNet, SHDB-AF, CPSC2021 and Icentia11k databases. [Authors to add further acknowledgements.] Use of artificial-intelligence tools: the study code, analyses and a first draft of this manuscript were prepared with the assistance of a large language model-based coding assistant (Claude, Anthropic). All analyses are fully scripted and reproducible from the public code; the authors take full responsibility for the content. [Authors to confirm and adapt this statement as required by the journal policy.]


## Funding

[None declared / to be completed by the authors.]


## Conflict of interest

[None declared / to be completed by the authors.]


## Consent

Not applicable. Only publicly available, de-identified data were analysed.


## Data availability

All databases are publicly available from PhysioNet (LTAFDB, AFDB, MITDB, NSRDB, NSR2DB, CHFDB, SHDB-AF v1.0.1, CPSC2021, Icentia11k). The complete code, configuration files, per-patient result files and the scripts regenerating every table, figure and number in this article are available at [public repository URL to be inserted; archived copy with DOI to be created on acceptance].


**Table 1 Databases, cohorts and reference rhythm characteristics**

| Database | Role | Country | Recordings | Patients | Hours analysed | Patients with AF | Patients with AFL | AF windows (%) |
|---|---|---|---|---|---|---|---|---|
| Long-Term AF Database | development | USA | 84 | 84 | 1897 | 83 | 0 | 58.1 |
| MIT-BIH AF Database | development | USA | 25 | 25 | 248 | 25 | 8 | 42.5 |
| MIT-BIH Arrhythmia Database | development | USA | 48 | 47 | 23 | 7 | 3 | 10.6 |
| MIT-BIH Normal Sinus Rhythm Database | development | USA | 18 | 18 | 378 | 0 | 0 | 0.0 |
| Normal Sinus Rhythm RR Interval Database | development | USA | 54 | 54 | 1200 | 0 | 0 | 0.0 |
| BIDMC Congestive Heart Failure Database | development | USA | 15 | 15 | 298 | 4 | 0 | 5.9 |
| SHDB-AF Japanese Holter AF database | external validation | Japan | 97 | 93 | 2297 | 72 | 12 | 23.8 |
| 4th China Physiological Signal Challenge 2021 | external validation | China | 1405 | 105 | 471 | 53 | 2 | 35.9 |
| Icentia11k continuous ECG (random subset) | external validation | Canada | 790 | 790 | 5808 | 50 | 25 | 5.9 |

Counts after exclusions (invalid RR intervals, unlabelled rhythm segments, one duplicate SHDB-AF recording). Windows are 60 consecutive valid RR intervals. AF, atrial fibrillation; AFL, atrial flutter.

**Table 2 Per-patient AF-burden mean absolute error (percentage points) by estimator and cohort, LightGBM detector**

| Estimator | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|
| CC | 3.55 ± 1.05 | 4.51 ± 0.12 | 3.85 ± 0.76 | 2.69 ± 0.35 | 2.99 ± 0.26 |
| CC-MF | 3.24 ± 1.22 | 4.31 ± 0.11 | 3.38 ± 0.67 | 2.46 ± 0.32 | 2.73 ± 0.23 |
| PCC | 4.51 ± 1.24 | 5.21 ± 0.52 | 5.54 ± 1.41 | 3.58 ± 0.51 | 3.94 ± 0.57 |
| PCC-iso | 4.16 ± 0.92 | 5.13 ± 0.42 | 5.50 ± 1.38 | 3.48 ± 0.48 | 3.85 ± 0.51 |
| ACC | 3.49 ± 1.03 | 4.73 ± 0.31 | 3.53 ± 0.71 | 2.59 ± 0.31 | 2.89 ± 0.22 |
| PACC | 3.73 ± 0.95 | 5.04 ± 0.25 | 4.26 ± 0.81 | 2.86 ± 0.26 | 3.21 ± 0.15 |
| EMQ | 3.10 ± 0.93 | 4.92 ± 0.52 | 3.78 ± 1.12 | 2.72 ± 0.29 | 3.04 ± 0.21 |
| HMM-src | 3.00 ± 1.02 | 4.53 ± 0.37 | 3.48 ± 1.02 | 2.82 ± 0.33 | 3.05 ± 0.29 |
| HMM-src[rawE] | 3.04 ± 1.32 | 4.24 ± 0.10 | 3.02 ± 0.43 | 2.25 ± 0.31 | 2.52 ± 0.22 |
| HMM-src[sel] (post hoc R1) | 1.69 ± nan | 4.38 ± nan | 3.56 ± nan | 2.33 ± nan | 2.65 ± nan |
| PA-HMMQ (pre-registered) | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.50 ± 1.06 | 2.84 ± 0.34 | 3.07 ± 0.30 |
| PA-HMMQ (final) | 3.04 ± 1.26 | 4.23 ± 0.11 | 2.88 ± 0.39 | 2.27 ± 0.33 | 2.52 ± 0.24 |
| PA-HMMQ[sel] (post hoc R1) | 1.96 ± nan | 4.40 ± nan | 3.69 ± nan | 2.42 ± nan | 2.74 ± nan |

Mean ± SD over five pre-specified seeds of the per-seed mean absolute error. Development test: held-out development patients (USA). CC, classify-and-count; CC-MF, CC after 3-window median filter; PCC, probabilistic CC; PCC-iso, PCC after isotonic recalibration on source calibration patients; ACC/PACC, adjusted (probabilistic) CC; EMQ, expectation–maximisation prior adjustment; HMM-src, hidden Markov model with fixed source dynamics; PA-HMMQ, patient-adaptive HMM quantifier.

**Table 3 Agreement with the reference AF burden in the pooled external cohorts (LightGBM detector)**

| Estimator | MAE (pp) | Median AE (pp) | RMSE (pp) | Bias (pp) | 95% LoA (pp) | Lin's CCC | False burden in AF-free patients (pp) | MAE in AF patients (pp) |
|---|---|---|---|---|---|---|---|---|
| CC | 2.99 ± 0.26 | 0.00 ± 0.00 | 12.52 ± 0.35 | 2.00 ± 0.41 | -22.23 to 26.24 | 0.900 ± 0.005 | 2.664 ± 0.388 | 4.49 ± 0.44 |
| CC-MF | 2.73 ± 0.23 | 0.00 ± 0.00 | 12.55 ± 0.31 | 1.86 ± 0.36 | -22.47 to 26.19 | 0.901 ± 0.004 | 2.447 ± 0.349 | 4.06 ± 0.40 |
| PCC | 3.94 ± 0.57 | 0.56 ± 0.66 | 12.53 ± 0.37 | 2.53 ± 0.07 | -21.53 to 26.60 | 0.897 ± 0.003 | 3.484 ± 0.376 | 6.05 ± 1.53 |
| PCC-iso | 3.85 ± 0.51 | 0.35 ± 0.54 | 12.80 ± 0.47 | 2.68 ± 0.31 | -21.85 to 27.22 | 0.894 ± 0.006 | 3.471 ± 0.438 | 5.59 ± 1.24 |
| ACC | 2.89 ± 0.22 | 0.00 ± 0.00 | 12.70 ± 0.36 | 2.05 ± 0.32 | -22.54 to 26.63 | 0.899 ± 0.005 | 2.586 ± 0.327 | 4.30 ± 0.41 |
| PACC | 3.21 ± 0.15 | 0.00 ± 0.00 | 12.84 ± 0.35 | 2.36 ± 0.22 | -22.39 to 27.11 | 0.897 ± 0.004 | 2.898 ± 0.253 | 4.67 ± 0.52 |
| EMQ | 3.04 ± 0.21 | 0.00 ± 0.00 | 13.84 ± 0.36 | 2.45 ± 0.25 | -24.26 to 29.17 | 0.884 ± 0.005 | 2.768 ± 0.272 | 4.32 ± 0.62 |
| HMM-src | 3.05 ± 0.29 | 0.00 ± 0.00 | 13.40 ± 0.57 | 2.49 ± 0.33 | -23.32 to 28.30 | 0.890 ± 0.009 | 2.887 ± 0.325 | 3.82 ± 0.48 |
| HMM-src[rawE] | 2.52 ± 0.22 | 0.00 ± 0.00 | 12.57 ± 0.31 | 1.65 ± 0.35 | -22.77 to 26.08 | 0.901 ± 0.004 | 2.216 ± 0.332 | 3.92 ± 0.32 |
| HMM-src[sel] | 2.65 ± nan | 0.00 ± nan | 12.45 ± nan | 1.93 ± nan | -22.19 to 26.05 | 0.903 ± nan | 2.394 ± nan | 3.86 ± nan |
| PA-HMMQ (pre-registered) | 3.07 ± 0.30 | 0.00 ± 0.00 | 13.38 ± 0.56 | 2.53 ± 0.34 | -23.24 to 28.29 | 0.890 ± 0.008 | 2.912 ± 0.340 | 3.81 ± 0.49 |
| PA-HMMQ (final) | 2.52 ± 0.24 | 0.00 ± 0.00 | 12.54 ± 0.33 | 1.70 ± 0.35 | -22.65 to 26.05 | 0.902 ± 0.005 | 2.237 ± 0.345 | 3.82 ± 0.28 |
| PA-HMMQ[sel] | 2.74 ± nan | 0.00 ± nan | 12.48 ± nan | 2.02 ± nan | -22.12 to 26.17 | 0.903 ± nan | 2.497 ± nan | 3.86 ± nan |

Mean ± SD over seeds. pp, percentage points; LoA, Bland–Altman limits of agreement; CCC, Lin's concordance correlation coefficient. False burden: mean estimated burden in patients without any reference AF.

**Table 4 Primary pre-specified comparison: final PA-HMMQ vs each comparator, pooled external cohorts (LightGBM)**

| Comparator | n patients | Mean AE proposed (pp) | Mean AE comparator (pp) | Mean paired diff (pp) [95% CI] | Median paired diff (pp) [95% CI] | Rank-biserial r | p (Holm) |
|---|---|---|---|---|---|---|---|
| CC | 988 | 2.52 | 2.99 | -0.47 [-0.56, -0.38] | 0.000 [0.000, 0.000] | -0.219 | 1e-08 |
| CC-MF | 988 | 2.52 | 2.73 | -0.21 [-0.27, -0.17] | 0.000 [0.000, 0.000] | 0.058 | 0.23 |
| PCC | 988 | 2.52 | 3.94 | -1.42 [-1.57, -1.28] | -0.543 [-0.559, -0.522] | -0.888 | 2.4e-128 |
| PCC-iso | 988 | 2.52 | 3.85 | -1.33 [-1.50, -1.16] | -0.302 [-0.348, -0.264] | -0.878 | 2.2e-125 |
| ACC | 988 | 2.52 | 2.89 | -0.37 [-0.46, -0.30] | 0.000 [0.000, 0.000] | 0.050 | 0.23 |
| PACC | 988 | 2.52 | 3.21 | -0.69 [-0.83, -0.57] | 0.000 [0.000, 0.000] | -0.068 | 0.2 |
| EMQ | 988 | 2.52 | 3.04 | -0.53 [-0.74, -0.33] | 0.000 [0.000, 0.000] | 0.353 | 3.6e-21 |
| HMM-src | 988 | 2.52 | 3.05 | -0.53 [-0.73, -0.35] | -0.000 [-0.000, -0.000] | -0.758 | 8.2e-94 |
| HMM-src[rawE] (post hoc, same emissions) | 988 | 2.52 | 2.52 | 0.00 [-0.02, 0.02] | -0.000 [-0.000, -0.000] | -0.579 | 6.4e-56 |

Unit of analysis: patient (absolute errors averaged over the five seeds). Two-sided Wilcoxon signed-rank tests, Holm-adjusted across the eight comparators. Paired difference = PA-HMMQ − comparator (negative favours PA-HMMQ); 95% CI by patient-level bootstrap (2000 resamples). Rank-biserial r < 0 indicates that PA-HMMQ has the smaller error in the majority of rank-weighted pairs.

**Table 5 Coverage and width of 90% per-patient burden intervals (LightGBM detector)**

| Method | Cohort | n | Coverage (mean ± SD over seeds) | Clopper–Pearson 95% CI | Coverage AF-free | Coverage AF | Mean width (pp) | Median width (pp) |
|---|---|---|---|---|---|---|---|---|
| CC + constant-width conformal | Development test | 49 | 0.898 ± 0.052 | 0.778–0.966 | 0.960 | 0.836 | 15.09 ± 15.12 | 12.62 ± 13.66 |
| CC + constant-width conformal | SHDB-AF | 93 | 0.867 ± 0.063 | 0.785–0.932 | 0.990 | 0.831 | 17.95 ± 17.67 | 17.96 ± 14.44 |
| CC + constant-width conformal | CPSC2021 | 105 | 0.872 ± 0.113 | 0.798–0.932 | 0.885 | 0.860 | 15.76 ± 15.97 | 13.42 ± 13.70 |
| CC + constant-width conformal | Icentia11k | 790 | 0.940 ± 0.032 | 0.922–0.956 | 0.939 | 0.956 | 13.26 ± 13.91 | 12.46 ± 13.71 |
| CC + constant-width conformal | Pooled external | 988 | 0.926 ± 0.042 | 0.908–0.942 | 0.937 | 0.875 | 13.97 ± 14.48 | 12.46 ± 13.71 |
| PA-HMMQ (pre-reg.) posterior 90% credible interval | Development test | 49 | 0.580 ± 0.031 | 0.422–0.712 | 0.927 | 0.230 | 0.32 ± 0.13 | 0.00 ± 0.00 |
| PA-HMMQ (pre-reg.) posterior 90% credible interval | SHDB-AF | 93 | 0.411 ± 0.039 | 0.308–0.515 | 0.952 | 0.253 | 0.37 ± 0.06 | 0.09 ± 0.03 |
| PA-HMMQ (pre-reg.) posterior 90% credible interval | CPSC2021 | 105 | 0.712 ± 0.033 | 0.618–0.798 | 0.765 | 0.660 | 1.47 ± 0.45 | 0.00 ± 0.00 |
| PA-HMMQ (pre-reg.) posterior 90% credible interval | Icentia11k | 790 | 0.900 ± 0.019 | 0.877–0.920 | 0.900 | 0.904 | 0.30 ± 0.04 | 0.00 ± 0.00 |
| PA-HMMQ (pre-reg.) posterior 90% credible interval | Pooled external | 988 | 0.834 ± 0.020 | 0.809–0.857 | 0.893 | 0.562 | 0.43 ± 0.08 | 0.00 ± 0.00 |
| PA-HMMQ (pre-reg.) + normalised conformal | Development test | 49 | 0.918 ± 0.043 | 0.804–0.977 | 0.976 | 0.862 | 5.22 ± 1.29 | 2.30 ± 0.29 |
| PA-HMMQ (pre-reg.) + normalised conformal | SHDB-AF | 93 | 0.845 ± 0.006 | 0.760–0.915 | 1.000 | 0.800 | 6.30 ± 0.70 | 5.14 ± 0.54 |
| PA-HMMQ (pre-reg.) + normalised conformal | CPSC2021 | 105 | 0.941 ± 0.010 | 0.880–0.979 | 0.915 | 0.966 | 12.16 ± 2.07 | 2.85 ± 0.65 |
| PA-HMMQ (pre-reg.) + normalised conformal | Icentia11k | 790 | 0.955 ± 0.006 | 0.939–0.969 | 0.955 | 0.964 | 4.29 ± 0.63 | 2.30 ± 0.29 |
| PA-HMMQ (pre-reg.) + normalised conformal | Pooled external | 988 | 0.943 ± 0.004 | 0.927–0.957 | 0.953 | 0.897 | 5.31 ± 0.71 | 2.30 ± 0.29 |
| PA-HMMQ (final) + constant-width conformal | Development test | 49 | 0.890 ± 0.072 | 0.778–0.966 | 0.976 | 0.803 | 12.16 ± 17.50 | 10.57 ± 16.04 |
| PA-HMMQ (final) + constant-width conformal | SHDB-AF | 93 | 0.862 ± 0.064 | 0.773–0.923 | 0.990 | 0.825 | 14.67 ± 20.55 | 14.41 ± 17.09 |
| PA-HMMQ (final) + constant-width conformal | CPSC2021 | 105 | 0.872 ± 0.090 | 0.798–0.932 | 0.923 | 0.823 | 12.42 ± 18.20 | 10.57 ± 16.04 |
| PA-HMMQ (final) + constant-width conformal | Icentia11k | 790 | 0.950 ± 0.022 | 0.932–0.964 | 0.949 | 0.964 | 10.91 ± 16.25 | 10.57 ± 16.04 |
| PA-HMMQ (final) + constant-width conformal | Pooled external | 988 | 0.933 ± 0.032 | 0.916–0.948 | 0.948 | 0.864 | 11.42 ± 16.87 | 10.57 ± 16.04 |
| PA-HMMQ (final) + normalised conformal (proposed) | Development test | 49 | 0.910 ± 0.049 | 0.804–0.977 | 0.976 | 0.845 | 4.35 ± 1.10 | 1.99 ± 0.48 |
| PA-HMMQ (final) + normalised conformal (proposed) | SHDB-AF | 93 | 0.843 ± 0.026 | 0.748–0.907 | 0.990 | 0.800 | 5.07 ± 1.22 | 4.41 ± 1.06 |
| PA-HMMQ (final) + normalised conformal (proposed) | CPSC2021 | 105 | 0.949 ± 0.041 | 0.892–0.984 | 0.950 | 0.947 | 9.57 ± 2.27 | 2.41 ± 0.67 |
| PA-HMMQ (final) + normalised conformal (proposed) | Icentia11k | 790 | 0.961 ± 0.011 | 0.945–0.973 | 0.961 | 0.972 | 3.05 ± 0.58 | 1.99 ± 0.48 |
| PA-HMMQ (final) + normalised conformal (proposed) | Pooled external | 988 | 0.949 ± 0.014 | 0.933–0.961 | 0.961 | 0.894 | 3.94 ± 0.76 | 1.99 ± 0.48 |

Target coverage 0.90. Conformal quantiles were computed on calibration-B patients only. Coverage: mean ± SD over seeds; Clopper–Pearson 95% CI computed from the seed-averaged coverage and the number of patients. Width in percentage points.

**Figure 1** Study pipeline. RR intervals derived from ambulatory ECG beat annotations are cut into 60-beat windows and scored by a window-level AF detector. The patient-adaptive hidden Markov quantifier (PA-HMMQ) treats the patient's window sequence as a two-state Markov chain whose rhythm dynamics are re-estimated for each patient (maximum-a-posteriori expectation–maximisation with a prior centred on source dynamics from calibration patients A), and returns the posterior expected burden. Posterior sampling gives a model-based standard deviation that is converted into a 90% conformal interval using calibration patients B. External cohorts are never used for training or calibration.
Alt text: Flow diagram with five boxes in a row: ambulatory ECG beat annotations to RR intervals, 60-beat windows, window detector producing AF probability, patient-adaptive HMM quantifier, and burden with 90% conformal interval. Three boxes below feed into the last three: calibration patients A, posterior sampling, calibration patients B.

**Figure 2** Per-patient AF-burden mean absolute error (percentage points) of nine estimators and the pre-registered PA-HMMQ variant in the development test set and three external cohorts, LightGBM detector. Points, mean over five seeds; bars, ±1 SD. Blue, PA-HMMQ variants. Abbreviations as in Table 2.
Alt text: Four dot-plot panels, one per cohort, listing ten burden estimators on the vertical axis and mean absolute error on the horizontal axis; the final PA-HMMQ has the lowest error in every panel.

**Figure 3** Bland–Altman plots of estimated versus reference AF burden in the pooled external cohorts for classify-and-count (left) and the final PA-HMMQ (right), LightGBM detector, estimates averaged over seeds. Hollow markers: patients with any reference atrial flutter. Solid line, mean difference; dashed lines, 95% limits of agreement. The diagonal band of points with large positive differences consists mainly of Icentia11k patients labelled atrial flutter, whose irregular ventricular response is classified as AF.
Alt text: Two scatter plots of difference against mean burden. Most points lie on zero; a diagonal line of hollow points with large positive differences corresponds to flutter patients; the right panel shows a slightly smaller bias.

**Figure 4** Empirical coverage (left) and mean width (right, log scale) of 90% per-patient burden intervals by method and cohort, LightGBM detector (mean ± SD over seeds). Dashed line, nominal coverage 0.90.
Alt text: Two dot-plot panels. Left: coverage of seven interval methods in four cohorts relative to a dashed 0.90 line. Right: mean interval width on a logarithmic axis, smallest for normalised conformal intervals of the final PA-HMMQ.

**Figure 5** Robustness of burden estimators in SHDB-AF to simulated missed and false R peaks, R-peak timing jitter and premature beats with compensatory pauses, for the LightGBM (left) and RRNet (right) detectors. Mean absolute error ± SD over seeds.
Alt text: Two line charts of mean absolute error across nine perturbation conditions for five estimators; errors rise with false R peaks and ectopy, and the final PA-HMMQ remains lowest or close to lowest in most conditions.

**Figure 6** Mean absolute error by reference burden stratum in the pooled external cohorts (LightGBM detector; logarithmic axis). Strata: AF-free (0%), >0–1%, >1–10%, >10–50% and >50% burden.
Alt text: Line chart with five burden strata on the horizontal axis and error on a logarithmic vertical axis for four estimators; errors are largest in intermediate strata.

## References

1. Chen LY, Chung MK, Allen LA, Ezekowitz M, Furie KL, McCabe P, et al. Atrial Fibrillation Burden: Moving Beyond Atrial Fibrillation as a Binary Entity: A Scientific Statement From the American Heart Association. Circulation 2018;137(20). doi:10.1161/CIR.0000000000000568
2. Go AS, Reynolds K, Yang J, Gupta N, Lenane J, Sung SH, et al. Association of Burden of Atrial Fibrillation With Risk of Ischemic Stroke in Adults With Paroxysmal Atrial Fibrillation. JAMA Cardiol 2018;3(7):601. doi:10.1001/jamacardio.2018.1176
3. Becher N, Metzner A, Toennis T, Kirchhof P, Schnabel RB. Atrial fibrillation burden: a new outcome predictor and therapeutic target. European Heart Journal 2024;45(31):2824-2838. doi:10.1093/eurheartj/ehae373
4. Kirchhof P, Toennis T, Goette A, Camm AJ, Diener HC, Becher N, et al. Anticoagulation with Edoxaban in Patients with Atrial High-Rate Episodes. N Engl J Med 2023;389(13):1167-1179. doi:10.1056/NEJMoa2303062
5. Healey JS, Lopes RD, Granger CB, Alings M, Rivard L, McIntyre WF, et al. Apixaban for Stroke Prevention in Subclinical Atrial Fibrillation. N Engl J Med 2024;390(2):107-117. doi:10.1056/NEJMoa2310234
6. Van Gelder IC, Rienstra M, Bunting KV, Casado-Arroyo R, Caso V, Crijns HJGM, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS). European Heart Journal 2024;45(36):3314-3414. doi:10.1093/eurheartj/ehae176
7. Chocron A, Oster J, Biton S, Mandel F, Elbaz M, Zeevi YY, et al. Remote Atrial Fibrillation Burden Estimation Using Deep Recurrent Neural Network. IEEE Trans. Biomed. Eng. 2021;68(8):2447-2455. doi:10.1109/TBME.2020.3042646
8. Biton S, Aldhafeeri M, Marcusohn E, Tsutsui K, Szwagier T, Elias A, et al. Generalizable and robust deep learning algorithm for atrial fibrillation diagnosis across geography, ages and sexes. npj Digit. Med. 2023;6(1):44. doi:10.1038/s41746-023-00791-1
9. Karimizadeh A, Mahnam A, Beheshti S, Moineau B, Alizadeh-Meghrazi M, Khaykin Y. Clinical performance of an atrial fibrillation burden tracking algorithm: Evaluation against reference public and clinical textile electrocardiographic datasets. Heart Rhythm O2 2026;7(6):1077-1085. doi:10.1016/j.hroo.2026.02.025
10. Haekal M, Nurul Khotimah S, Restu Fardian Suwandi G, Haryanto F. RR-interval-based atrial fibrillation detection and burden estimation: cross-dataset validation and calibration-aware probability analysis. Physiol. Meas. 2026;47(9):095002. doi:10.1088/1361-6579/ae99aa
11. Tateno K, Glass L. Automatic detection of atrial fibrillation using the coefficient of variation and density histograms of RR and ΔRR intervals. Med. Biol. Eng. Comput. 2001;39(6):664-671. doi:10.1007/BF02345439
12. Dash S, Chon KH, Lu S, Raeder EA. Automatic Real Time Detection of Atrial Fibrillation. Ann Biomed Eng 2009;37(9):1701-1709. doi:10.1007/s10439-009-9740-z
13. Lake DE, Moorman JR. Accurate estimation of entropy in very short physiological time series: the problem of atrial fibrillation detection in implanted ventricular devices. American Journal of Physiology-Heart and Circulatory Physiology 2011;300(1):H319-H325. doi:10.1152/ajpheart.00561.2010
14. Petrėnas A, Marozas V, Sörnmo L. Low-complexity detection of atrial fibrillation in continuous long-term monitoring. Computers in Biology and Medicine 2015;65:184-191. doi:10.1016/j.compbiomed.2015.01.019
15. Kennedy A, Finlay DD, Guldenring D, Bond RR, Moran K, McLaughlin J. Automated detection of atrial fibrillation using R-R intervals and multivariate-based classification. Journal of Electrocardiology 2016;49(6):871-876. doi:10.1016/j.jelectrocard.2016.07.033
16. Faust O, Shenfield A, Kareem M, San TR, Fujita H, Acharya UR. Automated detection of atrial fibrillation using long short-term memory network with RR interval signals. Computers in Biology and Medicine 2018;102:327-335. doi:10.1016/j.compbiomed.2018.07.001
17. Andersen RS, Peimankar A, Puthusserypady S. A deep learning approach for real-time detection of atrial fibrillation. Expert Systems with Applications 2019;115:465-473. doi:10.1016/j.eswa.2018.08.011
18. Forman G. Quantifying counts and costs via classification. Data Min Knowl Disc 2008;17(2):164-206. doi:10.1007/s10618-008-0097-y
19. Saerens M, Latinne P, Decaestecker C. Adjusting the Outputs of a Classifier to New a Priori Probabilities: A Simple Procedure. Neural Computation 2002;14(1):21-41. doi:10.1162/089976602753284446
20. Bella A, Ferri C, Hernandez-Orallo J, Ramirez-Quintana MJ. Quantification via Probability Estimators. 2010 IEEE International Conference on Data Mining 2010:737-742. doi:10.1109/ICDM.2010.75
21. González P, Castaño A, Chawla NV, Coz JJD. A Review on Quantification Learning. ACM Comput. Surv. 2018;50(5):1-40. doi:10.1145/3117807
22. Esuli A, Fabris A, Moreo A, Sebastiani F. Learning to Quantify. The Information Retrieval Series. Cham/New York: Springer; 2023. doi:10.1007/978-3-031-20467-8
23. Vovk V, Gammerman A, Shafer G. Algorithmic Learning in a Random World. Cham/New York: Springer; 2005. doi:10.1007/b106715
24. Lei J, G’Sell M, Rinaldo A, Tibshirani RJ, Wasserman L. Distribution-Free Predictive Inference for Regression. Journal of the American Statistical Association 2018;113(523):1094-1111. doi:10.1080/01621459.2017.1307116
25. Angelopoulos AN, Bates S. Conformal Prediction: A Gentle Introduction. Foundations and Trends® in Machine Learning 2023;16(4):494-591. doi:10.1561/2200000101
26. Abbasi T, Abbas A, Mehmood UH. Local Conformal Auditing Exposes and Restores Reliability of AI-ECG Atrial Fibrillation Detection Under External Deployment Shift. Heart Rhythm 2026. doi:10.1016/j.hrthm.2026.10.064
27. El Allam O, Hamlich M. Per-class conformal risk control for multi-label ECG classification: achieving clinically-justified false negative rate guarantees. Physiol. Meas. 2026;47(10):105021. doi:10.1088/1361-6579/aeb3c6
28. Moody GB, Mark RG. A new method for detecting atrial fibrillation using R-R intervals. Comput Cardiol 1983;10:227–230.
29. Young B, Brodnick D, Spaulding R. A comparative study of a hidden Markov model detector for atrial fibrillation. In: Neural Networks for Signal Processing IX: Proceedings of the 1999 IEEE Signal Processing Society Workshop. IEEE; 1999. p.468–476. doi:10.1109/NNSP.1999.788166
30. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ 2024;385:e078378. doi:10.1136/bmj-2023-078378
31. Svennberg E, Han JK, Caiani EG, Engelhardt S, Ernst S, Friedman P, et al. State of the Art of Artificial Intelligence in Clinical Electrophysiology in 2025: A Scientific Statement of the European Heart Rhythm Association (EHRA) of the ESC, the Heart Rhythm Society (HRS), and the ESC Working Group on E-Cardiology. Europace 2025;27(5):euaf071. doi:10.1093/europace/euaf071
32. Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PC, Mark RG, et al. PhysioBank, PhysioToolkit, and PhysioNet. Circulation 2000;101(23). doi:10.1161/01.CIR.101.23.e215
33. Petrutiu S, Sahakian AV, Swiryn S. Abrupt changes in fibrillatory wave characteristics at the termination of paroxysmal atrial fibrillation in humans. EP Europace 2007;9(7):466-470. doi:10.1093/europace/eum096
34. Moody G, Mark R. The impact of the MIT-BIH Arrhythmia Database. IEEE Eng. Med. Biol. Mag. 2001;20(3):45-50. doi:10.1109/51.932724
35. Baim DS, Colucci WS, Monrad ES, Smith HS, Wright RF, Lanoue A, et al. Survival of patients with severe congestive heart failure treated with oral milrinone. Journal of the American College of Cardiology 1986;7(3):661-670. doi:10.1016/S0735-1097(86)80478-8
36. Tsutsui K, Brimer SB, Ben-Moshe N, Sellal JM, Oster J, Mori H, et al. SHDB-AF: a Japanese Holter ECG database of atrial fibrillation. Sci Data 2025;12(1):454. doi:10.1038/s41597-025-04777-4
37. Wang X, Ma C, Zhang X, Gao H, Clifford G, Liu C. Paroxysmal Atrial Fibrillation Events Detection from Dynamic ECG Recordings: The 4th China Physiological Signal Challenge 2021 [dataset/preprint]. PhysioNet; 2021. doi:10.13026/ksya-qw89
38. Tan S, Ortiz-Gagné S, Beaudoin-Gagnon N, Fecteau P, Courville A, Bengio Y, et al. Icentia11k Single Lead Continuous Raw Electrocardiogram Dataset [dataset/preprint]. PhysioNet; 2022. doi:10.13026/kk0v-r952
39. Tan S, Androz G, Chamseddine A, Fecteau P, Courville A, Bengio Y, et al. Icentia11K: An Unsupervised Representation Learning Dataset for Arrhythmia Subtype Discovery [dataset/preprint]. arXiv; 2019. doi:10.48550/arXiv.1910.09570
40. Rabiner LR. A tutorial on hidden Markov models and selected applications in speech recognition. Proc IEEE 1989;77(2):257–286. doi:10.1109/5.18626
41. Carter CK, Kohn R. On Gibbs sampling for state space models. Biometrika 1994;81(3):541–553. doi:10.1093/biomet/81.3.541
42. Wilcoxon F. Individual Comparisons by Ranking Methods. Biometrics Bulletin 1945;1(6):80. doi:10.2307/3001968
43. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70. Available from: https://www.jstor.org/stable/4615733
44. Kerby DS. The Simple Difference Formula: An Approach to Teaching Nonparametric Correlation. Comprehensive Psychology 2014;3:11.IT.3.1. doi:10.2466/11.IT.3.1
45. Bland JM, Altman DG. Statistical methods for assessing agreement between two methods of clinical measurement. Lancet 1986;1(8476):307–310. doi:10.1016/S0140-6736(86)90837-8
46. Lin LIK. A Concordance Correlation Coefficient to Evaluate Reproducibility. Biometrics 1989;45(1):255. doi:10.2307/2532051
47. Hennings E, Coslovsky M, Paladini RE, Aeschbacher S, Knecht S, Schlageter V, et al. Assessment of the atrial fibrillation burden in Holter electrocardiogram recordings using artificial intelligence. Cardiovascular Digital Health Journal 2023;4(2):41-47. doi:10.1016/j.cvdhj.2023.01.003
48. Aguilar M, Macle L, Chamieh R, Khairy P, Deyell MW, Bennett RG, et al. Wearable smartwatches for atrial fibrillation detection and burden estimation after ablation: comparison with continuous monitoring. Europace 2026;28(9):euaf280. doi:10.1093/europace/euaf280
