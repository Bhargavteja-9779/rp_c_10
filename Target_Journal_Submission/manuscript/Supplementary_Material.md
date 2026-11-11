# Estimating atrial fibrillation burden as a per-patient quantification problem with distribution-free uncertainty intervals: development and multinational external validation


## Supplementary material

## S1. Pre-registration and design decisions The full analysis plan (candidate topics considered, stress test, novelty map, hypotheses, research questions, splits, seeds, fixed hyper-parameters, endpoints and statistical tests) was committed to version control before any model was trained and is provided as the file S1_research_design_preregistration.md. One amendment (A1) was recorded after a one-seed pipeline check and before the full analysis: the emission model of PA-HMMQ would be selected on development patients only (calibration-B and development test patients, LightGBM, mean per-patient absolute error). The rule selected the probability-emission variant (development error 1.381 vs 1.938 pp). Deviations from the plan: (i) reduced-training-data and window-length analyses omitted Icentia11k for computational reasons; (ii) the analysis of patients without atrial flutter is post hoc; (iii) one SHDB-AF recording was excluded after the leakage audit (below).

## S2. Data processing and leakage audit Only beat and rhythm annotation files were downloaded and verified against PhysioNet SHA-256 checksums. CPSC2021 records of patient 51 (11 records) were not retrievable from the repository (HTTP 404) and are absent. In Icentia11k, beats outside labelled rhythm regions were treated as unlabelled and excluded. The automated audit hashed every 60-beat window (RR rounded to 8 ms) and fingerprinted every recording. SHDB-AF Data_ID 020 was an exact RR-level duplicate of Data_ID 005 (same Subject_ID; metadata Holter dates 2021 and 2024) and was removed; after removal no recording-level duplicates remained, and 2 individual windows (of 928477) were shared between different patients, consistent with chance identity of very regular rhythms. Patient-level splits were verified disjoint for every seed, and no development patient occurred in an external cohort. The SHDB-AF metadata columns are Data_ID/Subject_ID (not the names given in the database README); patients with two recordings were aggregated.

## S3. Detector details Features (16). Mean RR; SDNN; coefficient of variation; RMSSD/mean RR; pNN50; pNN20; median |ΔRR|/mean RR; interquartile range/median RR; turning-point ratio; normalised Shannon entropy of the 16-bin RR histogram; Poincaré SD1/mean RR, SD2/mean RR and SD1/SD2; a coefficient-of-sample-entropy-type irregularity measure (sample entropy with m = 2, r = 0.2·SD, plus log-normalisation by mean RR); fraction of sign changes of ΔRR; min/max RR ratio. Classical-LR used normalised RMSSD, Shannon entropy and turning-point ratio with standardisation fitted on training patients. LightGBM: up to 400 trees, learning rate 0.05, 31 leaves, row and column subsampling 0.8, early stopping (50 rounds) on inner-validation patients. RRNet: input two channels (log RR minus window mean; ΔRR), three 1-D convolutional blocks (32 channels, kernel 5, batch normalisation, ReLU, residual connections), bidirectional GRU (32 units per direction), mean and max pooling, two-layer head with dropout 0.2; AdamW (learning rate 10⁻³, weight decay 10⁻⁴), cosine schedule, batch 512, ≤12 epochs, early stopping (patience 3) on inner-validation binary cross-entropy; 27,681 parameters. RRNet is a re-implementation inspired by ArNet/ArNet2, not the original code or weights.

## S4. PA-HMMQ and interval details Hidden states zt ∈ {0 (non-AF), 1 (AF)} for consecutive windows of a recording; emissions ek(xt) are fixed: in the final variant e1 = pt, e0 = 1 − pt (p clipped to [10⁻⁶, 1 − 10⁻⁶]); in the pre-registered variant ek is a Laplace-smoothed 50-bin histogram density of logit(p) among calibration-A windows of class k. The source transition matrix and initial distribution are add-one-smoothed frequencies of reference window labels in calibration-A sequences. For each patient i, expectation–maximisation alternates forward–backward smoothing (all recordings of the patient share Ai, πi) with the MAP updates Ai(k,l) ∝ Σξ(k,l) + κAsrc(k,l) and πi(k) ∝ Σγ1(k) + κπsrc(k), until the relative log-likelihood change is <10⁻⁶ (≤50 iterations). Burden is Σdtγt(1)/Σdt. Posterior samples of the whole state path are drawn by forward-filtering backward-sampling at the converged parameters; σ̂i is the standard deviation of the duration-weighted sampled burden. EMQ is recovered by removing temporal dependence and HMM-src by fixing Ai = Asrc.

## S5. Supplementary tables and figures Supplementary Tables S1–S14 and Figures S1–S8 follow. All values are generated automatically from the result files in the code repository.


**Table S2 Window-level detector performance (mean ± SD over seeds)**

| Detector | Cohort | auroc | auprc | sensitivity | specificity | f1 | ece | brier |
|---|---|---|---|---|---|---|---|---|
| Classical-LR | Development test | 0.968 ± nan | 0.894 ± nan | 0.903 ± nan | 0.945 ± nan | 0.896 ± nan | 0.039 ± nan | 0.056 ± nan |
| Classical-LR | SHDB-AF | 0.884 ± nan | 0.619 ± nan | 0.859 ± nan | 0.879 ± nan | 0.765 ± nan | 0.077 ± nan | 0.107 ± nan |
| Classical-LR | CPSC2021 | 0.880 ± nan | 0.655 ± nan | 0.948 ± nan | 0.781 ± nan | 0.810 ± nan | 0.117 ± nan | 0.134 ± nan |
| Classical-LR | Icentia11k | 0.961 ± nan | 0.448 ± nan | 0.956 ± nan | 0.928 ± nan | 0.614 ± nan | 0.103 ± nan | 0.060 ± nan |
| LightGBM | Development test | 0.997 ± nan | 0.994 ± nan | 0.968 ± nan | 0.975 ± nan | 0.959 ± nan | 0.010 ± nan | 0.020 ± nan |
| LightGBM | SHDB-AF | 0.973 ± nan | 0.908 ± nan | 0.895 ± nan | 0.953 ± nan | 0.875 ± nan | 0.045 ± nan | 0.052 ± nan |
| LightGBM | CPSC2021 | 0.992 ± nan | 0.982 ± nan | 0.981 ± nan | 0.933 ± nan | 0.934 ± nan | 0.037 ± nan | 0.038 ± nan |
| LightGBM | Icentia11k | 0.990 ± nan | 0.799 ± nan | 0.979 ± nan | 0.970 ± nan | 0.797 ± nan | 0.028 ± nan | 0.026 ± nan |
| RRNet | Development test | 0.998 ± nan | 0.995 ± nan | 0.991 ± nan | 0.971 ± nan | 0.966 ± nan | 0.016 ± nan | 0.018 ± nan |
| RRNet | SHDB-AF | 0.971 ± nan | 0.909 ± nan | 0.918 ± nan | 0.944 ± nan | 0.875 ± nan | 0.048 ± nan | 0.054 ± nan |
| RRNet | CPSC2021 | 0.990 ± nan | 0.968 ± nan | 0.996 ± nan | 0.910 ± nan | 0.924 ± nan | 0.058 ± nan | 0.046 ± nan |
| RRNet | Icentia11k | 0.987 ± nan | 0.726 ± nan | 0.989 ± nan | 0.955 ± nan | 0.729 ± nan | 0.045 ± nan | 0.037 ± nan |

Threshold 0.5. ECE, expected calibration error (15 bins).

**Table S3 Per-patient AF-burden MAE (pp) by estimator, Classical-LR detector**

| Estimator | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|
| CC | 8.49 ± nan | 10.55 ± nan | 18.07 ± nan | 7.66 ± nan | 9.04 ± nan |
| CC-MF | 8.07 ± nan | 10.27 ± nan | 17.87 ± nan | 7.31 ± nan | 8.71 ± nan |
| PCC | 14.54 ± nan | 12.63 ± nan | 22.29 ± nan | 13.04 ± nan | 13.99 ± nan |
| PCC-iso | 12.98 ± nan | 11.54 ± nan | 21.69 ± nan | 10.90 ± nan | 12.11 ± nan |
| ACC | 8.77 ± nan | 11.57 ± nan | 18.90 ± nan | 7.40 ± nan | 9.02 ± nan |
| PACC | 11.64 ± nan | 12.78 ± nan | 21.12 ± nan | 9.14 ± nan | 10.76 ± nan |
| EMQ | 10.65 ± nan | 12.14 ± nan | 19.96 ± nan | 9.27 ± nan | 10.68 ± nan |
| HMM-src | 10.95 ± nan | 11.21 ± nan | 17.75 ± nan | 10.03 ± nan | 10.96 ± nan |
| PA-HMMQ (pre-registered) | 10.21 ± nan | 11.28 ± nan | 17.79 ± nan | 10.15 ± nan | 11.07 ± nan |
| PA-HMMQ (final) | 7.43 ± nan | 9.73 ± nan | 17.37 ± nan | 6.71 ± nan | 8.13 ± nan |

Mean ± SD over seeds.

**Table S4 Per-patient AF-burden MAE (pp) by estimator, RRNet detector**

| Estimator | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|
| CC | 2.87 ± nan | 5.19 ± nan | 6.43 ± nan | 4.32 ± nan | 4.63 ± nan |
| CC-MF | 2.81 ± nan | 4.84 ± nan | 6.22 ± nan | 4.09 ± nan | 4.38 ± nan |
| PCC | 3.29 ± nan | 5.59 ± nan | 7.35 ± nan | 4.79 ± nan | 5.14 ± nan |
| PCC-iso | 3.64 ± nan | 5.43 ± nan | 6.55 ± nan | 4.43 ± nan | 4.75 ± nan |
| ACC | 3.29 ± nan | 5.58 ± nan | 6.38 ± nan | 4.17 ± nan | 4.54 ± nan |
| PACC | 3.26 ± nan | 5.86 ± nan | 6.89 ± nan | 4.41 ± nan | 4.81 ± nan |
| EMQ | 2.55 ± nan | 5.15 ± nan | 4.97 ± nan | 3.10 ± nan | 3.49 ± nan |
| HMM-src | 1.46 ± nan | 4.27 ± nan | 4.22 ± nan | 3.20 ± nan | 3.41 ± nan |
| PA-HMMQ (pre-registered) | 1.51 ± nan | 4.24 ± nan | 4.21 ± nan | 3.19 ± nan | 3.40 ± nan |
| PA-HMMQ (final) | 2.46 ± nan | 4.48 ± nan | 5.63 ± nan | 3.74 ± nan | 4.01 ± nan |

Mean ± SD over seeds.

**Table S5 Ablation of PA-HMMQ components (LightGBM, MAE in pp)**

| Variant | Calibration B | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|---|
| PA-HMMQ | 1.83 ± nan | 2.04 ± nan | 4.55 ± nan | 3.79 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[k=0] | 1.72 ± nan | 2.04 ± nan | 4.54 ± nan | 3.86 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[k=100] | 1.82 ± nan | 2.04 ± nan | 4.55 ± nan | 3.81 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[k=1] | 1.82 ± nan | 2.04 ± nan | 4.55 ± nan | 3.86 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[k=30] | 1.83 ± nan | 2.04 ± nan | 4.55 ± nan | 3.79 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[k=3] | 1.83 ± nan | 2.04 ± nan | 4.55 ± nan | 3.83 ± nan | 2.55 ± nan | 2.87 ± nan |
| PA-HMMQ[rawE,k=0] | 1.10 ± nan | 1.70 ± nan | 4.35 ± nan | 3.35 ± nan | 2.26 ± nan | 2.57 ± nan |
| PA-HMMQ[rawE,k=100] | 1.13 ± nan | 1.64 ± nan | 4.36 ± nan | 3.50 ± nan | 2.24 ± nan | 2.58 ± nan |
| PA-HMMQ[rawE,k=1] | 1.09 ± nan | 1.70 ± nan | 4.35 ± nan | 3.36 ± nan | 2.26 ± nan | 2.57 ± nan |
| PA-HMMQ[rawE,k=30] | 1.10 ± nan | 1.68 ± nan | 4.36 ± nan | 3.45 ± nan | 2.25 ± nan | 2.58 ± nan |
| PA-HMMQ[rawE,k=3] | 1.04 ± nan | 1.71 ± nan | 4.35 ± nan | 3.37 ± nan | 2.26 ± nan | 2.57 ± nan |
| PA-HMMQ[rawE] | 1.05 ± nan | 1.70 ± nan | 4.35 ± nan | 3.39 ± nan | 2.26 ± nan | 2.57 ± nan |
| CC | 1.33 ± nan | 2.70 ± nan | 4.72 ± nan | 4.86 ± nan | 2.77 ± nan | 3.18 ± nan |
| EMQ | 2.17 ± nan | 2.74 ± nan | 5.50 ± nan | 4.76 ± nan | 2.45 ± nan | 2.98 ± nan |
| HMM-src | 1.83 ± nan | 2.04 ± nan | 4.58 ± nan | 3.82 ± nan | 2.54 ± nan | 2.87 ± nan |
| HMM-src[rawE] | 1.15 ± nan | 1.62 ± nan | 4.37 ± nan | 3.51 ± nan | 2.23 ± nan | 2.57 ± nan |

k, prior strength κ in pseudo-transitions (κ=10 pre-specified); rawE, detector probability used as emission likelihood (final variant); HMM-src, no per-patient adaptation (κ→∞); EMQ, per-patient prior adaptation without temporal model; CC, no quantification.

**Table S6 MAE (pp) by reference burden stratum, pooled external cohorts (LightGBM)**

| Estimator | 0 (AF-free) (n=813) | (0,1%] (n=16) | (1,10%] (n=30) | (10,50%] (n=35) | >50% (n=94) |
|---|---|---|---|---|---|
| CC | 2.89 | 6.58 | 2.21 | 6.01 | 4.36 |
| CC-MF | 2.61 | 6.24 | 1.88 | 5.89 | 3.85 |
| PCC-iso | 3.99 | 7.58 | 3.77 | 6.09 | 9.58 |
| ACC | 2.67 | 6.45 | 2.77 | 6.86 | 3.96 |
| EMQ | 2.56 | 6.42 | 2.10 | 9.87 | 3.75 |
| HMM-src | 2.66 | 6.09 | 2.41 | 6.36 | 2.92 |
| PA-HMMQ (pre-registered) | 2.68 | 6.07 | 2.40 | 6.37 | 2.79 |
| PA-HMMQ (final) | 2.31 | 5.83 | 1.77 | 5.34 | 3.55 |

Mean over seeds.

**Table S7 Classification of patients by burden thresholds, pooled external cohorts (LightGBM)**

| Estimator | present_30s sens | present_30s spec | ge1pct sens | ge1pct spec | ge10pct sens | ge10pct spec |
|---|---|---|---|---|---|---|
| CC | 0.994 ± nan | 0.709 ± nan | 1.000 ± nan | 0.832 ± nan | 0.977 ± nan | 0.936 ± nan |
| CC-MF | 0.988 ± nan | 0.800 ± nan | 1.000 ± nan | 0.867 ± nan | 0.977 ± nan | 0.942 ± nan |
| PCC-iso | 1.000 ± nan | 0.040 ± nan | 1.000 ± nan | 0.470 ± nan | 0.977 ± nan | 0.917 ± nan |
| ACC | 0.913 ± nan | 0.881 ± nan | 0.969 ± nan | 0.893 ± nan | 0.969 ± nan | 0.939 ± nan |
| EMQ | 0.931 ± nan | 0.929 ± nan | 0.962 ± nan | 0.936 ± nan | 0.969 ± nan | 0.953 ± nan |
| HMM-src | 0.971 ± nan | 0.875 ± nan | 0.987 ± nan | 0.899 ± nan | 0.977 ± nan | 0.943 ± nan |
| PA-HMMQ (pre-registered) | 0.960 ± nan | 0.890 ± nan | 0.981 ± nan | 0.900 ± nan | 0.977 ± nan | 0.942 ± nan |
| PA-HMMQ (final) | 0.960 ± nan | 0.892 ± nan | 0.987 ± nan | 0.908 ± nan | 0.977 ± nan | 0.956 ± nan |

present_30s: ≥30 s of AF in the analysed recording; ge1pct/ge10pct: burden ≥1%/≥10%. Mean ± SD over seeds.

**Table S8 Influence of atrial flutter (LightGBM, pooled external)**

| Estimator | MAE vs AF reference (pp) | MAE vs AF+AFL reference (pp) | MAE excluding patients with any AFL, n=949 (post hoc) |
|---|---|---|---|
| CC | 3.18 ± nan | 2.24 ± nan | 1.84 ± nan |
| CC-MF | 2.88 ± nan | 1.94 ± nan | 1.54 ± nan |
| PCC | 3.55 ± nan | 2.64 ± nan | 2.25 ± nan |
| PCC-iso | 4.65 ± nan | 3.89 ± nan | 3.44 ± nan |
| ACC | 3.01 ± nan | 2.04 ± nan | 1.63 ± nan |
| PACC | 3.21 ± nan | 2.24 ± nan | 1.83 ± nan |
| EMQ | 2.98 ± nan | 2.00 ± nan | 1.60 ± nan |
| HMM-src | 2.87 ± nan | 1.91 ± nan | 1.52 ± nan |
| PA-HMMQ (pre-registered) | 2.87 ± nan | 1.90 ± nan | 1.52 ± nan |
| PA-HMMQ (final) | 2.57 ± nan | 1.66 ± nan | 1.24 ± nan |

The AF+AFL reference counts flutter time as arrhythmia time. The analysis excluding patients with any flutter is post hoc.

**Table S11 Sensitivity to training-set size and window length (LightGBM, MAE in pp)**

| Setting | Estimator | Development test | SHDB-AF | CPSC2021 |
|---|---|---|---|---|
| 100% training data, W=60 (main) | CC | 2.70 ± nan | 4.72 ± nan | 4.86 ± nan |
| 100% training data, W=60 (main) | CC-MF | 2.12 ± nan | 4.49 ± nan | 4.22 ± nan |
| 100% training data, W=60 (main) | PCC-iso | 4.74 ± nan | 5.80 ± nan | 7.69 ± nan |
| 100% training data, W=60 (main) | ACC | 2.77 ± nan | 5.26 ± nan | 4.38 ± nan |
| 100% training data, W=60 (main) | EMQ | 2.74 ± nan | 5.50 ± nan | 4.76 ± nan |
| 100% training data, W=60 (main) | HMM-src | 2.04 ± nan | 4.58 ± nan | 3.82 ± nan |
| 100% training data, W=60 (main) | PA-HMMQ (pre-registered) | 2.04 ± nan | 4.55 ± nan | 3.79 ± nan |
| 100% training data, W=60 (main) | PA-HMMQ (final) | 1.70 ± nan | 4.35 ± nan | 3.39 ± nan |

Reduced-data and window-length runs used SHDB-AF and CPSC2021 as external cohorts (Icentia11k omitted for computational reasons).

**Table S12 Subgroup MAE (pp) in SHDB-AF by sex and age (LightGBM)**

| Estimator | Subgroup | n | MAE (pp) |
|---|---|---|---|
| CC | female | 42 | 3.70 |
| CC | male | 51 | 5.55 |
| CC | age < 69 | 45 | 2.00 |
| CC | age ≥ 69 | 48 | 7.27 |
| PA-HMMQ (pre-registered) | female | 42 | 3.22 |
| PA-HMMQ (pre-registered) | male | 51 | 5.64 |
| PA-HMMQ (pre-registered) | age < 69 | 45 | 1.59 |
| PA-HMMQ (pre-registered) | age ≥ 69 | 48 | 7.32 |
| PA-HMMQ (final) | female | 42 | 3.42 |
| PA-HMMQ (final) | male | 51 | 5.12 |
| PA-HMMQ (final) | age < 69 | 45 | 1.63 |
| PA-HMMQ (final) | age ≥ 69 | 48 | 6.91 |

Age split at the cohort median.

**Table S13 The 15 external patients with the largest absolute error of the final PA-HMMQ (LightGBM, seed-averaged)**

| patient | ae | err | true_burden | ectopy_sv | ectopy_v | afl | hours | db |
|---|---|---|---|---|---|---|---|---|
| icentia_p05828 | 100.000 | 100.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.274 | icentia11k |
| icentia_p05149 | 100.000 | 100.000 | 0.000 | 0.000 | 0.023 | 1.000 | 8.921 | icentia11k |
| icentia_p01292 | 100.000 | 100.000 | 0.000 | 0.000 | 0.017 | 1.000 | 6.351 | icentia11k |
| icentia_p01304 | 100.000 | 100.000 | 0.000 | 0.000 | 0.031 | 1.000 | 1.236 | icentia11k |
| icentia_p07973 | 99.997 | 99.997 | 0.000 | 0.000 | 0.000 | 1.000 | 5.662 | icentia11k |
| icentia_p00921 | 97.878 | 97.878 | 0.000 | 0.000 | 0.162 | 1.000 | 2.271 | icentia11k |
| icentia_p03332 | 95.538 | 95.538 | 0.000 | 0.000 | 0.000 | 1.000 | 7.721 | icentia11k |
| icentia_p09800 | 92.920 | 92.920 | 0.000 | 0.000 | 0.000 | 1.000 | 10.668 | icentia11k |
| icentia_p06999 | 87.721 | 87.721 | 0.000 | 0.417 | 0.006 | 0.000 | 7.884 | icentia11k |
| icentia_p08389 | 85.769 | 85.769 | 0.000 | 0.000 | 0.001 | 0.858 | 6.546 | icentia11k |
| cpsc_II_54 | 84.045 | -84.045 | 1.000 | 0.000 | 0.001 | 0.000 | 0.708 | cpsc2021 |
| icentia_p10993 | 80.609 | 80.609 | 0.000 | 0.000 | 0.000 | 0.806 | 7.194 | icentia11k |
| icentia_p06217 | 70.800 | 70.800 | 0.000 | 0.016 | 0.003 | 0.708 | 7.050 | icentia11k |
| shdb_5210865 | 69.276 | 69.276 | 0.000 | 0.000 | 0.000 | 0.723 | 23.996 | shdb-af |
| icentia_p10163 | 66.629 | 66.629 | 0.000 | 0.000 | 0.000 | 1.000 | 9.463 | icentia11k |

ae, absolute error (pp); err, signed error (pp); true_burden, fraction; ectopy and AFL as fractions of beats/time.

**Table S14 All paired comparisons (all detectors, cohorts and both PA-HMMQ variants)**

| Detector | Proposed | Cohort | Comparator | n patients | Mean AE proposed (pp) | Mean AE comparator (pp) | Mean paired diff (pp) [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Classical-LR | PA-HMMQ (final) | Pooled external | CC | 988 | 8.13 | 9.04 | -0.91 [-1.11, -0.73] | 5.3e-14 |
| Classical-LR | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 8.13 | 8.71 | -0.58 [-0.72, -0.44] | 0.93 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PCC | 988 | 8.13 | 13.99 | -5.86 [-6.27, -5.44] | 2e-112 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 8.13 | 12.11 | -3.98 [-4.45, -3.52] | 1.7e-87 |
| Classical-LR | PA-HMMQ (final) | Pooled external | ACC | 988 | 8.13 | 9.02 | -0.89 [-1.10, -0.69] | 3.1e-09 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PACC | 988 | 8.13 | 10.76 | -2.63 [-2.99, -2.29] | 2e-09 |
| Classical-LR | PA-HMMQ (final) | Pooled external | EMQ | 988 | 8.13 | 10.68 | -2.55 [-3.11, -2.02] | 0.00045 |
| Classical-LR | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 8.13 | 10.96 | -2.83 [-3.46, -2.16] | 1.9e-92 |
| Classical-LR | PA-HMMQ (final) | Development test | CC | 49 | 7.43 | 8.49 | -1.06 [-2.46, 0.07] | 0.15 |
| Classical-LR | PA-HMMQ (final) | Development test | CC-MF | 49 | 7.43 | 8.07 | -0.64 [-1.61, 0.08] | 0.94 |
| Classical-LR | PA-HMMQ (final) | Development test | PCC | 49 | 7.43 | 14.54 | -7.11 [-9.79, -4.73] | 5.7e-07 |
| Classical-LR | PA-HMMQ (final) | Development test | PCC-iso | 49 | 7.43 | 12.98 | -5.55 [-8.35, -2.92] | 2.4e-05 |
| Classical-LR | PA-HMMQ (final) | Development test | ACC | 49 | 7.43 | 8.77 | -1.34 [-2.50, -0.36] | 0.77 |
| Classical-LR | PA-HMMQ (final) | Development test | PACC | 49 | 7.43 | 11.64 | -4.21 [-6.48, -2.17] | 0.0069 |
| Classical-LR | PA-HMMQ (final) | Development test | EMQ | 49 | 7.43 | 10.65 | -3.22 [-7.59, 0.31] | 0.94 |
| Classical-LR | PA-HMMQ (final) | Development test | HMM-src | 49 | 7.43 | 10.95 | -3.52 [-9.52, 1.24] | 0.11 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | CC | 93 | 9.73 | 10.55 | -0.82 [-1.26, -0.39] | 0.00093 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 9.73 | 10.27 | -0.54 [-0.83, -0.24] | 0.013 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 9.73 | 12.63 | -2.90 [-3.88, -1.89] | 5.4e-07 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 9.73 | 11.54 | -1.81 [-3.06, -0.50] | 2.8e-05 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 9.73 | 11.57 | -1.84 [-2.58, -1.08] | 0.00028 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 9.73 | 12.78 | -3.05 [-4.05, -2.03] | 9.9e-07 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 9.73 | 12.14 | -2.41 [-3.51, -1.31] | 0.00012 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 9.73 | 11.21 | -1.48 [-2.84, -0.12] | 0.00093 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | CC | 105 | 17.37 | 18.07 | -0.71 [-1.54, 0.09] | 0.51 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 17.37 | 17.87 | -0.50 [-1.16, 0.16] | 0.86 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 17.37 | 22.29 | -4.93 [-6.65, -3.22] | 2.1e-06 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 17.37 | 21.69 | -4.32 [-6.24, -2.36] | 0.00022 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 17.37 | 18.90 | -1.53 [-2.48, -0.62] | 0.51 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 17.37 | 21.12 | -3.75 [-5.09, -2.39] | 5.4e-05 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 17.37 | 19.96 | -2.59 [-4.47, -0.55] | 0.12 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 17.37 | 17.75 | -0.38 [-2.96, 2.44] | 0.0032 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | CC | 790 | 6.71 | 7.66 | -0.95 [-1.17, -0.74] | 2.3e-11 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 6.71 | 7.31 | -0.59 [-0.76, -0.44] | 0.23 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PCC | 790 | 6.71 | 13.04 | -6.33 [-6.76, -5.89] | 2.8e-101 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 6.71 | 10.90 | -4.19 [-4.68, -3.70] | 2e-85 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | ACC | 790 | 6.71 | 7.40 | -0.69 [-0.90, -0.50] | 6.4e-22 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PACC | 790 | 6.71 | 9.14 | -2.43 [-2.83, -2.07] | 0.015 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 6.71 | 9.27 | -2.56 [-3.17, -1.99] | 2.6e-13 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 6.71 | 10.03 | -3.31 [-4.06, -2.65] | 3.8e-97 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 11.07 | 9.04 | 2.03 [1.44, 2.60] | 5.3e-22 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 11.07 | 8.71 | 2.36 [1.76, 2.94] | 8.3e-63 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 11.07 | 13.99 | -2.92 [-3.55, -2.27] | 7.9e-44 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 11.07 | 12.11 | -1.04 [-1.60, -0.48] | 8.1e-28 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 11.07 | 9.02 | 2.05 [1.44, 2.64] | 8.1e-73 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 11.07 | 10.76 | 0.31 [-0.24, 0.83] | 3.1e-15 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 11.07 | 10.68 | 0.39 [-0.03, 0.77] | 3.7e-47 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 11.07 | 10.96 | 0.11 [0.04, 0.17] | 3.1e-15 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | CC | 49 | 10.21 | 8.49 | 1.72 [-2.69, 7.17] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | CC-MF | 49 | 10.21 | 8.07 | 2.14 [-2.33, 7.65] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PCC | 49 | 10.21 | 14.54 | -4.33 [-8.63, 0.13] | 0.0011 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PCC-iso | 49 | 10.21 | 12.98 | -2.77 [-6.69, 1.53] | 0.016 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | ACC | 49 | 10.21 | 8.77 | 1.44 [-3.04, 6.92] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PACC | 49 | 10.21 | 11.64 | -1.43 [-5.47, 2.76] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | EMQ | 49 | 10.21 | 10.65 | -0.44 [-2.62, 1.46] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | HMM-src | 49 | 10.21 | 10.95 | -0.74 [-1.63, -0.05] | 0.53 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 11.28 | 10.55 | 0.73 [-0.41, 1.89] | 0.61 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 11.28 | 10.27 | 1.01 [-0.22, 2.23] | 0.023 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 11.28 | 12.63 | -1.34 [-2.76, 0.06] | 0.0092 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 11.28 | 11.54 | -0.26 [-1.73, 1.20] | 0.31 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 11.28 | 11.57 | -0.28 [-1.58, 0.88] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 11.28 | 12.78 | -1.50 [-2.82, -0.28] | 0.17 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 11.28 | 12.14 | -0.86 [-2.06, 0.24] | 0.62 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 11.28 | 11.21 | 0.07 [-0.06, 0.22] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 17.79 | 18.07 | -0.28 [-2.94, 2.28] | 0.64 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 17.79 | 17.87 | -0.08 [-2.81, 2.53] | 0.041 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 17.79 | 22.29 | -4.50 [-7.44, -1.53] | 0.075 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 17.79 | 21.69 | -3.90 [-6.64, -1.08] | 0.058 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 17.79 | 18.90 | -1.11 [-3.83, 1.40] | 0.075 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 17.79 | 21.12 | -3.33 [-6.13, -0.81] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 17.79 | 19.96 | -2.17 [-4.39, -0.29] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 17.79 | 17.75 | 0.04 [-0.27, 0.35] | 0.53 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 10.15 | 7.66 | 2.49 [1.89, 3.07] | 1.6e-24 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 10.15 | 7.31 | 2.84 [2.24, 3.47] | 2.8e-65 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 10.15 | 13.04 | -2.90 [-3.57, -2.27] | 6.2e-43 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 10.15 | 10.90 | -0.76 [-1.35, -0.22] | 2.2e-28 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 10.15 | 7.40 | 2.74 [2.14, 3.38] | 2.9e-89 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 10.15 | 9.14 | 1.00 [0.50, 1.51] | 1.2e-25 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 10.15 | 9.27 | 0.87 [0.47, 1.26] | 4e-68 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 10.15 | 10.03 | 0.12 [0.06, 0.19] | 5.2e-18 |
| LightGBM | PA-HMMQ (final) | Pooled external | CC | 988 | 2.57 | 3.18 | -0.60 [-0.73, -0.49] | 0.0079 |
| LightGBM | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 2.57 | 2.88 | -0.31 [-0.39, -0.24] | 7.1e-06 |
| LightGBM | PA-HMMQ (final) | Pooled external | PCC | 988 | 2.57 | 3.55 | -0.98 [-1.15, -0.82] | 4.8e-115 |
| LightGBM | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 2.57 | 4.65 | -2.07 [-2.29, -1.86] | 3.3e-130 |
| LightGBM | PA-HMMQ (final) | Pooled external | ACC | 988 | 2.57 | 3.01 | -0.43 [-0.55, -0.32] | 5.6e-26 |
| LightGBM | PA-HMMQ (final) | Pooled external | PACC | 988 | 2.57 | 3.21 | -0.63 [-0.79, -0.50] | 1.6e-14 |
| LightGBM | PA-HMMQ (final) | Pooled external | EMQ | 988 | 2.57 | 2.98 | -0.41 [-0.64, -0.20] | 5.8e-49 |
| LightGBM | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 2.57 | 2.87 | -0.29 [-0.43, -0.17] | 5.6e-106 |
| LightGBM | PA-HMMQ (final) | Development test | CC | 49 | 1.70 | 2.70 | -1.00 [-1.90, -0.33] | 0.017 |
| LightGBM | PA-HMMQ (final) | Development test | CC-MF | 49 | 1.70 | 2.12 | -0.42 [-0.90, -0.05] | 0.81 |
| LightGBM | PA-HMMQ (final) | Development test | PCC | 49 | 1.70 | 3.18 | -1.48 [-2.66, -0.57] | 4.5e-06 |
| LightGBM | PA-HMMQ (final) | Development test | PCC-iso | 49 | 1.70 | 4.74 | -3.04 [-4.73, -1.63] | 2.1e-08 |
| LightGBM | PA-HMMQ (final) | Development test | ACC | 49 | 1.70 | 2.77 | -1.07 [-1.80, -0.47] | 0.31 |
| LightGBM | PA-HMMQ (final) | Development test | PACC | 49 | 1.70 | 3.06 | -1.36 [-2.36, -0.56] | 0.44 |
| LightGBM | PA-HMMQ (final) | Development test | EMQ | 49 | 1.70 | 2.74 | -1.03 [-2.43, -0.00] | 0.87 |
| LightGBM | PA-HMMQ (final) | Development test | HMM-src | 49 | 1.70 | 2.04 | -0.34 [-1.28, 0.35] | 0.046 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | CC | 93 | 4.35 | 4.72 | -0.36 [-0.61, -0.13] | 0.0045 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 4.35 | 4.49 | -0.14 [-0.30, 0.01] | 0.026 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 4.35 | 4.99 | -0.64 [-0.97, -0.31] | 3.4e-05 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 4.35 | 5.80 | -1.45 [-1.95, -0.93] | 2.9e-11 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 4.35 | 5.26 | -0.90 [-1.30, -0.55] | 3.1e-06 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 4.35 | 5.44 | -1.08 [-1.55, -0.66] | 7.1e-07 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 4.35 | 5.50 | -1.14 [-2.26, -0.18] | 2.9e-05 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 4.35 | 4.58 | -0.23 [-0.70, 0.16] | 0.026 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | CC | 105 | 3.39 | 4.86 | -1.47 [-2.22, -0.83] | 0.00068 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 3.39 | 4.22 | -0.83 [-1.34, -0.40] | 0.46 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 3.39 | 5.80 | -2.41 [-3.36, -1.61] | 3.9e-10 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 3.39 | 7.69 | -4.30 [-5.43, -3.29] | 1.6e-12 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 3.39 | 4.38 | -1.00 [-1.64, -0.41] | 0.71 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 3.39 | 4.96 | -1.57 [-2.42, -0.81] | 0.71 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 3.39 | 4.76 | -1.37 [-2.58, -0.34] | 0.12 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 3.39 | 3.82 | -0.43 [-1.09, 0.45] | 2.5e-07 |
| LightGBM | PA-HMMQ (final) | Icentia11k | CC | 790 | 2.26 | 2.77 | -0.52 [-0.64, -0.40] | 0.55 |
| LightGBM | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 2.26 | 2.51 | -0.26 [-0.34, -0.19] | 4.7e-15 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PCC | 790 | 2.26 | 3.08 | -0.83 [-0.98, -0.68] | 2.1e-108 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 2.26 | 4.10 | -1.85 [-2.07, -1.63] | 3.2e-111 |
| LightGBM | PA-HMMQ (final) | Icentia11k | ACC | 790 | 2.26 | 2.56 | -0.30 [-0.41, -0.20] | 1.6e-52 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PACC | 790 | 2.26 | 2.71 | -0.46 [-0.59, -0.33] | 1.2e-36 |
| LightGBM | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 2.26 | 2.45 | -0.20 [-0.39, -0.02] | 5.6e-84 |
| LightGBM | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 2.26 | 2.54 | -0.28 [-0.41, -0.17] | 6.6e-113 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 2.87 | 3.18 | -0.31 [-0.44, -0.17] | 0.97 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 2.87 | 2.88 | -0.01 [-0.13, 0.12] | 4.2e-19 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 2.87 | 3.55 | -0.68 [-0.84, -0.53] | 5.2e-98 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 2.87 | 4.65 | -1.78 [-2.01, -1.54] | 6.5e-113 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 2.87 | 3.01 | -0.14 [-0.25, -0.01] | 8.8e-42 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 2.87 | 3.21 | -0.34 [-0.47, -0.22] | 1.1e-24 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 2.87 | 2.98 | -0.11 [-0.30, 0.06] | 1.6e-57 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 2.87 | 2.87 | 0.00 [-0.03, 0.03] | 1.1e-77 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | CC | 49 | 2.04 | 2.70 | -0.66 [-1.78, 0.19] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | CC-MF | 49 | 2.04 | 2.12 | -0.07 [-0.92, 0.71] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PCC | 49 | 2.04 | 3.18 | -1.14 [-2.46, -0.20] | 0.0019 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PCC-iso | 49 | 2.04 | 4.74 | -2.70 [-4.64, -1.16] | 4.4e-05 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | ACC | 49 | 2.04 | 2.77 | -0.72 [-1.68, 0.06] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PACC | 49 | 2.04 | 3.06 | -1.02 [-2.12, -0.20] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | EMQ | 49 | 2.04 | 2.74 | -0.69 [-1.69, 0.03] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | HMM-src | 49 | 2.04 | 2.04 | 0.00 [-0.07, 0.06] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 4.55 | 4.72 | -0.17 [-0.55, 0.29] | 0.037 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 4.55 | 4.49 | 0.06 [-0.31, 0.50] | 0.32 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 4.55 | 4.99 | -0.44 [-0.88, 0.07] | 0.00014 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 4.55 | 5.80 | -1.25 [-1.93, -0.49] | 3.3e-09 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 4.55 | 5.26 | -0.71 [-1.16, -0.26] | 0.00014 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 4.55 | 5.44 | -0.89 [-1.36, -0.42] | 3.5e-05 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 4.55 | 5.50 | -0.95 [-1.79, -0.19] | 0.0017 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 4.55 | 4.58 | -0.03 [-0.08, 0.01] | 0.15 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 3.79 | 4.86 | -1.07 [-1.88, -0.31] | 0.053 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 3.79 | 4.22 | -0.43 [-1.25, 0.30] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 3.79 | 5.80 | -2.01 [-2.97, -1.16] | 1.3e-07 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 3.79 | 7.69 | -3.90 [-5.19, -2.71] | 1e-09 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 3.79 | 4.38 | -0.60 [-1.33, 0.04] | 0.4 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 3.79 | 4.96 | -1.17 [-1.97, -0.45] | 1 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 3.79 | 4.76 | -0.97 [-2.04, 0.02] | 0.57 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 3.79 | 3.82 | -0.03 [-0.22, 0.15] | 0.013 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 2.55 | 2.77 | -0.22 [-0.34, -0.10] | 0.0035 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 2.55 | 2.51 | 0.04 [-0.06, 0.15] | 9.1e-31 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 2.55 | 3.08 | -0.54 [-0.68, -0.39] | 4.2e-93 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 2.55 | 4.10 | -1.56 [-1.79, -1.32] | 4.5e-98 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 2.55 | 2.56 | -0.01 [-0.10, 0.10] | 2.6e-70 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 2.55 | 2.71 | -0.16 [-0.27, -0.05] | 2.1e-48 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 2.55 | 2.45 | 0.10 [-0.05, 0.24] | 3.2e-93 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 2.55 | 2.54 | 0.01 [-0.02, 0.04] | 8.6e-87 |
| RRNet | PA-HMMQ (final) | Pooled external | CC | 988 | 4.01 | 4.63 | -0.62 [-0.76, -0.49] | 0.068 |
| RRNet | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 4.01 | 4.38 | -0.38 [-0.47, -0.29] | 5.2e-05 |
| RRNet | PA-HMMQ (final) | Pooled external | PCC | 988 | 4.01 | 5.14 | -1.13 [-1.32, -0.95] | 1e-115 |
| RRNet | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 4.01 | 4.75 | -0.74 [-0.99, -0.47] | 2.4e-83 |
| RRNet | PA-HMMQ (final) | Pooled external | ACC | 988 | 4.01 | 4.54 | -0.53 [-0.65, -0.40] | 8.3e-14 |
| RRNet | PA-HMMQ (final) | Pooled external | PACC | 988 | 4.01 | 4.81 | -0.80 [-0.98, -0.64] | 2e-08 |
| RRNet | PA-HMMQ (final) | Pooled external | EMQ | 988 | 4.01 | 3.49 | 0.52 [0.32, 0.72] | 5e-72 |
| RRNet | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 4.01 | 3.41 | 0.60 [0.44, 0.77] | 9.1e-22 |
| RRNet | PA-HMMQ (final) | Development test | CC | 49 | 2.46 | 2.87 | -0.41 [-1.03, 0.04] | 1 |
| RRNet | PA-HMMQ (final) | Development test | CC-MF | 49 | 2.46 | 2.81 | -0.36 [-0.92, -0.00] | 1 |
| RRNet | PA-HMMQ (final) | Development test | PCC | 49 | 2.46 | 3.29 | -0.83 [-1.36, -0.36] | 0.00054 |
| RRNet | PA-HMMQ (final) | Development test | PCC-iso | 49 | 2.46 | 3.64 | -1.19 [-2.31, -0.07] | 0.0023 |
| RRNet | PA-HMMQ (final) | Development test | ACC | 49 | 2.46 | 3.29 | -0.83 [-1.55, -0.28] | 1 |
| RRNet | PA-HMMQ (final) | Development test | PACC | 49 | 2.46 | 3.26 | -0.81 [-1.42, -0.29] | 1 |
| RRNet | PA-HMMQ (final) | Development test | EMQ | 49 | 2.46 | 2.55 | -0.09 [-1.30, 1.02] | 1 |
| RRNet | PA-HMMQ (final) | Development test | HMM-src | 49 | 2.46 | 1.46 | 0.99 [0.05, 2.38] | 0.51 |
| RRNet | PA-HMMQ (final) | SHDB-AF | CC | 93 | 4.48 | 5.19 | -0.71 [-1.15, -0.34] | 1.2e-05 |
| RRNet | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 4.48 | 4.84 | -0.35 [-0.58, -0.16] | 0.0018 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 4.48 | 5.59 | -1.11 [-1.70, -0.57] | 8.4e-09 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 4.48 | 5.43 | -0.95 [-1.69, -0.05] | 3.4e-08 |
| RRNet | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 4.48 | 5.58 | -1.09 [-1.56, -0.65] | 2.1e-05 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 4.48 | 5.86 | -1.38 [-2.00, -0.84] | 1.4e-05 |
| RRNet | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 4.48 | 5.15 | -0.67 [-1.30, -0.09] | 0.049 |
| RRNet | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 4.48 | 4.27 | 0.21 [0.01, 0.43] | 0.096 |
| RRNet | PA-HMMQ (final) | CPSC2021 | CC | 105 | 5.63 | 6.43 | -0.80 [-1.38, -0.24] | 1 |
| RRNet | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 5.63 | 6.22 | -0.59 [-0.94, -0.24] | 1 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 5.63 | 7.35 | -1.72 [-2.52, -0.93] | 5.3e-08 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 5.63 | 6.55 | -0.92 [-2.24, 0.54] | 3.5e-05 |
| RRNet | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 5.63 | 6.38 | -0.75 [-1.27, -0.24] | 1 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 5.63 | 6.89 | -1.26 [-2.01, -0.56] | 1 |
| RRNet | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 5.63 | 4.97 | 0.66 [-0.20, 1.58] | 6e-05 |
| RRNet | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 5.63 | 4.22 | 1.41 [0.60, 2.36] | 1 |
| RRNet | PA-HMMQ (final) | Icentia11k | CC | 790 | 3.74 | 4.32 | -0.59 [-0.72, -0.46] | 0.43 |
| RRNet | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 3.74 | 4.09 | -0.35 [-0.45, -0.26] | 3.8e-12 |
| RRNet | PA-HMMQ (final) | Icentia11k | PCC | 790 | 3.74 | 4.79 | -1.05 [-1.24, -0.87] | 6.8e-103 |
| RRNet | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 3.74 | 4.43 | -0.69 [-0.93, -0.44] | 9.9e-74 |
| RRNet | PA-HMMQ (final) | Icentia11k | ACC | 790 | 3.74 | 4.17 | -0.43 [-0.56, -0.31] | 3.7e-30 |
| RRNet | PA-HMMQ (final) | Icentia11k | PACC | 790 | 3.74 | 4.41 | -0.67 [-0.84, -0.52] | 2.6e-20 |
| RRNet | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 3.74 | 3.10 | 0.64 [0.42, 0.86] | 3.2e-94 |
| RRNet | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 3.74 | 3.20 | 0.54 [0.38, 0.70] | 3.3e-34 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 3.40 | 4.63 | -1.23 [-1.46, -1.01] | 0.0048 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 3.40 | 4.38 | -0.99 [-1.20, -0.79] | 0.0061 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 3.40 | 5.14 | -1.74 [-2.01, -1.48] | 4.8e-123 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 3.40 | 4.75 | -1.35 [-1.56, -1.13] | 3.1e-106 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 3.40 | 4.54 | -1.14 [-1.38, -0.92] | 1.2e-08 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 3.40 | 4.81 | -1.41 [-1.69, -1.16] | 0.00014 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 3.40 | 3.49 | -0.09 [-0.27, 0.06] | 7e-57 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 3.40 | 3.41 | -0.01 [-0.03, 0.02] | 3.8e-77 |
| RRNet | PA-HMMQ (pre-registered) | Development test | CC | 49 | 1.51 | 2.87 | -1.36 [-3.32, -0.01] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | CC-MF | 49 | 1.51 | 2.81 | -1.31 [-3.23, -0.04] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PCC | 49 | 1.51 | 3.29 | -1.78 [-3.60, -0.45] | 0.0026 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PCC-iso | 49 | 1.51 | 3.64 | -2.14 [-3.34, -1.05] | 9.1e-07 |
| RRNet | PA-HMMQ (pre-registered) | Development test | ACC | 49 | 1.51 | 3.29 | -1.78 [-3.80, -0.36] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PACC | 49 | 1.51 | 3.26 | -1.76 [-3.65, -0.35] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | EMQ | 49 | 1.51 | 2.55 | -1.04 [-2.45, -0.07] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | HMM-src | 49 | 1.51 | 1.46 | 0.04 [0.01, 0.10] | 1 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 4.24 | 5.19 | -0.95 [-1.54, -0.47] | 1.2e-05 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 4.24 | 4.84 | -0.59 [-0.99, -0.25] | 0.0002 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 4.24 | 5.59 | -1.35 [-2.10, -0.71] | 2.5e-08 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 4.24 | 5.43 | -1.19 [-1.89, -0.35] | 4.4e-09 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 4.24 | 5.58 | -1.33 [-1.96, -0.78] | 3.8e-07 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 4.24 | 5.86 | -1.62 [-2.40, -0.96] | 8.2e-08 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 4.24 | 5.15 | -0.91 [-1.64, -0.24] | 0.0022 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 4.24 | 4.27 | -0.03 [-0.07, 0.01] | 0.17 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 4.21 | 6.43 | -2.22 [-3.24, -1.28] | 0.023 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 4.21 | 6.22 | -2.00 [-3.01, -1.12] | 0.17 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 4.21 | 7.35 | -3.13 [-4.25, -2.09] | 2.9e-11 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 4.21 | 6.55 | -2.34 [-3.37, -1.31] | 9.1e-10 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 4.21 | 6.38 | -2.17 [-3.22, -1.22] | 0.71 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 4.21 | 6.89 | -2.68 [-3.85, -1.59] | 0.71 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 4.21 | 4.97 | -0.76 [-1.85, 0.10] | 0.11 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 4.21 | 4.22 | -0.00 [-0.18, 0.21] | 0.0017 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 3.19 | 4.32 | -1.13 [-1.38, -0.90] | 0.92 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 3.19 | 4.09 | -0.90 [-1.12, -0.69] | 8.1e-10 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 3.19 | 4.79 | -1.60 [-1.89, -1.33] | 2.9e-107 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 3.19 | 4.43 | -1.23 [-1.44, -1.02] | 3.5e-90 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 3.19 | 4.17 | -0.98 [-1.23, -0.74] | 9.2e-24 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 3.19 | 4.41 | -1.22 [-1.50, -0.96] | 2.2e-16 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 3.19 | 3.10 | 0.09 [-0.04, 0.22] | 6.9e-87 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 3.19 | 3.20 | -0.01 [-0.03, 0.01] | 6.4e-85 |

As Table 4.

**Figure S1** Distribution of reference AF burden (A) and analysed monitoring time per patient (B) in the development test set (seed 11) and the external cohorts.
Alt text: Two cumulative distribution plots, one per panel, with four lines for the cohorts.

**Figure S2** Window-level ROC (top; x-axis truncated at 0.3) and precision–recall (bottom) curves of the three detectors in each cohort (seed 11).
Alt text: Grid of eight small line charts showing ROC and precision-recall curves for three detectors in four cohorts.

**Figure S3** Row-normalised window-level confusion matrices of the LightGBM detector (all seeds pooled).
Alt text: Four two-by-two heat maps with proportions of correctly and incorrectly classified AF and non-AF windows.

**Figure S4** RRNet training and inner-validation binary cross-entropy per epoch for the five seeds.
Alt text: Line chart of loss against epoch, ten lines for five seeds.

**Figure S5** Mean absolute burden error as a function of the prior strength κ for calibrated-histogram and probability emissions, in the development test set and pooled external cohorts (LightGBM; mean ± SD over seeds).
Alt text: Line chart with six κ values on the horizontal axis and error on the vertical axis for four combinations of emission model and cohort.

**Figure S6** Mean paired difference in per-patient absolute burden error between the final PA-HMMQ and each comparator in the pooled external cohorts (LightGBM), with bootstrap 95% CI and Holm-adjusted P values.
Alt text: Forest plot with eight comparators, all point estimates left of zero.

**Figure S7** Per-patient absolute error of the final PA-HMMQ versus the proportion of ectopic beats (A) and atrial flutter burden (B), pooled external cohorts (log–log axes).
Alt text: Two scatter plots on logarithmic axes; large errors cluster at high flutter burden.

**Figure S8** Median CPU time per 24-h recording of each pipeline component.
Alt text: Horizontal bar chart of milliseconds per 24-hour recording for feature extraction, detector inference and burden estimators on a logarithmic axis.

## References


