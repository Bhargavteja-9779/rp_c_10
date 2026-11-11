# Temporal quantification of atrial fibrillation burden with distribution-free uncertainty intervals: development and multinational external validation


## Supplementary material


### S1. Pre-registration and design decisions

The full analysis plan (candidate topics considered, stress test, novelty map, hypotheses, research questions, splits, seeds, fixed hyper-parameters, endpoints and statistical tests) was committed to version control before any model was trained and is provided as the file S1_research_design_preregistration.md. One amendment (A1) was recorded after a one-seed pipeline check and before the full analysis: the emission model of PA-HMMQ would be selected on development patients only (calibration-B and development test patients, LightGBM, mean per-patient absolute error). The rule selected the probability-emission variant (development error 2.858 vs 3.186 pp). Deviations from the plan: (i) reduced-training-data and window-length analyses omitted Icentia11k for computational reasons; (ii) the analysis of patients without atrial flutter is post hoc; (iii) one SHDB-AF recording was excluded after the leakage audit (below).


### S2. Data processing and leakage audit

Only beat and rhythm annotation files were downloaded and verified against PhysioNet SHA-256 checksums. CPSC2021 records of patient 51 (11 records) were not retrievable from the repository (HTTP 404) and are absent. In Icentia11k, beats outside labelled rhythm regions were treated as unlabelled and excluded. The automated audit hashed every 60-beat window (RR rounded to 8 ms) and fingerprinted every recording. SHDB-AF Data_ID 020 was an exact RR-level duplicate of Data_ID 005 (same Subject_ID; metadata Holter dates 2021 and 2024) and was removed; after removal no recording-level duplicates remained, and 2 individual windows (of 928477) were shared between different patients, consistent with chance identity of very regular rhythms. Patient-level splits were verified disjoint for every seed, and no development patient occurred in an external cohort. The SHDB-AF metadata columns are Data_ID/Subject_ID (not the names given in the database README); patients with two recordings were aggregated.


### S3. Detector details

Features (16). Mean RR; SDNN; coefficient of variation; RMSSD/mean RR; pNN50; pNN20; median |ΔRR|/mean RR; interquartile range/median RR; turning-point ratio; normalised Shannon entropy of the 16-bin RR histogram; Poincaré SD1/mean RR, SD2/mean RR and SD1/SD2; a coefficient-of-sample-entropy-type irregularity measure (sample entropy with m = 2, r = 0.2·SD, plus log-normalisation by mean RR); fraction of sign changes of ΔRR; min/max RR ratio. Classical-LR used normalised RMSSD, Shannon entropy and turning-point ratio with standardisation fitted on training patients. LightGBM: up to 400 trees, learning rate 0.05, 31 leaves, row and column subsampling 0.8, early stopping (50 rounds) on inner-validation patients. RRNet: input two channels (log RR minus window mean; ΔRR), three 1-D convolutional blocks (32 channels, kernel 5, batch normalisation, ReLU, residual connections), bidirectional GRU (32 units per direction), mean and max pooling, two-layer head with dropout 0.2; AdamW (learning rate 10⁻³, weight decay 10⁻⁴), cosine schedule, batch 512, ≤12 epochs, early stopping (patience 3) on inner-validation binary cross-entropy; 27,681 parameters. RRNet is a re-implementation inspired by ArNet/ArNet2, not the original code or weights.


### S4. PA-HMMQ and interval details

Hidden states zt ∈ {0 (non-AF), 1 (AF)} for consecutive windows of a recording; emissions ek(xt) are fixed: in the final variant e1 = pt, e0 = 1 − pt (p clipped to [10⁻⁶, 1 − 10⁻⁶]); in the pre-registered variant ek is a Laplace-smoothed 50-bin histogram density of logit(p) among calibration-A windows of class k. The source transition matrix and initial distribution are add-one-smoothed frequencies of reference window labels in calibration-A sequences. For each patient i, expectation–maximisation alternates forward–backward smoothing (all recordings of the patient share Ai, πi) with the MAP updates Ai(k,l) ∝ Σξ(k,l) + κAsrc(k,l) and πi(k) ∝ Σγ1(k) + κπsrc(k), until the relative log-likelihood change is <10⁻⁶ (≤50 iterations). Burden is Σdtγt(1)/Σdt. Posterior samples of the whole state path are drawn by forward-filtering backward-sampling at the converged parameters; σ̂i is the standard deviation of the duration-weighted sampled burden. EMQ is recovered by removing temporal dependence and HMM-src by fixing Ai = Asrc.


### S5. Supplementary tables and figures

Supplementary Tables S1–S14 and Figures S1–S8 follow. All values are generated automatically from the result files in the code repository.


**Table S2 Window-level detector performance (mean ± SD over seeds)**

| Detector | Cohort | auroc | auprc | sensitivity | specificity | f1 | ece | brier |
|---|---|---|---|---|---|---|---|---|
| Classical-LR | Development test | 0.959 ± 0.012 | 0.875 ± 0.036 | 0.851 ± 0.039 | 0.951 ± 0.009 | 0.873 ± 0.022 | 0.058 ± 0.027 | 0.067 ± 0.008 |
| Classical-LR | SHDB-AF | 0.884 ± 0.001 | 0.628 ± 0.010 | 0.837 ± 0.023 | 0.889 ± 0.009 | 0.763 ± 0.005 | 0.068 ± 0.010 | 0.104 ± 0.003 |
| Classical-LR | CPSC2021 | 0.884 ± 0.004 | 0.663 ± 0.010 | 0.926 ± 0.025 | 0.798 ± 0.018 | 0.810 ± 0.005 | 0.100 ± 0.019 | 0.129 ± 0.005 |
| Classical-LR | Icentia11k | 0.961 ± 0.000 | 0.457 ± 0.011 | 0.931 ± 0.028 | 0.933 ± 0.007 | 0.622 ± 0.009 | 0.099 ± 0.009 | 0.057 ± 0.005 |
| LightGBM | Development test | 0.992 ± 0.005 | 0.986 ± 0.009 | 0.909 ± 0.046 | 0.983 ± 0.012 | 0.936 ± 0.023 | 0.032 ± 0.013 | 0.035 ± 0.011 |
| LightGBM | SHDB-AF | 0.969 ± 0.003 | 0.902 ± 0.007 | 0.881 ± 0.011 | 0.960 ± 0.004 | 0.878 ± 0.003 | 0.035 ± 0.012 | 0.051 ± 0.001 |
| LightGBM | CPSC2021 | 0.992 ± 0.001 | 0.980 ± 0.004 | 0.976 ± 0.009 | 0.954 ± 0.013 | 0.949 ± 0.010 | 0.025 ± 0.007 | 0.029 ± 0.005 |
| LightGBM | Icentia11k | 0.990 ± 0.001 | 0.776 ± 0.021 | 0.974 ± 0.006 | 0.972 ± 0.004 | 0.804 ± 0.016 | 0.030 ± 0.002 | 0.024 ± 0.003 |
| RRNet | Development test | 0.992 ± 0.007 | 0.987 ± 0.012 | 0.917 ± 0.060 | 0.983 ± 0.011 | 0.940 ± 0.029 | 0.032 ± 0.017 | 0.033 ± 0.014 |
| RRNet | SHDB-AF | 0.973 ± 0.001 | 0.910 ± 0.005 | 0.908 ± 0.012 | 0.952 ± 0.008 | 0.881 ± 0.006 | 0.045 ± 0.003 | 0.051 ± 0.002 |
| RRNet | CPSC2021 | 0.990 ± 0.002 | 0.967 ± 0.008 | 0.989 ± 0.012 | 0.939 ± 0.023 | 0.943 ± 0.015 | 0.036 ± 0.017 | 0.035 ± 0.009 |
| RRNet | Icentia11k | 0.986 ± 0.001 | 0.686 ± 0.029 | 0.981 ± 0.012 | 0.963 ± 0.009 | 0.762 ± 0.037 | 0.036 ± 0.010 | 0.032 ± 0.006 |

Threshold 0.5. ECE, expected calibration error (15 bins).

**Table S3 Per-patient AF-burden MAE (pp) by estimator, Classical-LR detector**

| Estimator | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|
| CC | 7.71 ± 0.48 | 9.94 ± 0.54 | 17.34 ± 0.81 | 7.20 ± 0.57 | 8.54 ± 0.56 |
| CC-MF | 7.28 ± 0.52 | 9.69 ± 0.50 | 16.95 ± 0.98 | 6.79 ± 0.57 | 8.14 ± 0.58 |
| PCC | 13.40 ± 1.13 | 12.31 ± 0.54 | 22.10 ± 0.95 | 12.99 ± 0.68 | 13.90 ± 0.65 |
| PCC-iso | 10.87 ± 1.66 | 11.13 ± 0.35 | 20.82 ± 0.75 | 10.55 ± 0.85 | 11.70 ± 0.74 |
| ACC | 7.28 ± 0.91 | 11.01 ± 0.51 | 17.75 ± 1.20 | 6.84 ± 0.34 | 8.40 ± 0.41 |
| PACC | 8.95 ± 1.66 | 12.16 ± 0.69 | 20.05 ± 1.37 | 8.87 ± 0.61 | 10.37 ± 0.65 |
| EMQ | 7.36 ± 2.15 | 11.42 ± 0.48 | 18.32 ± 1.30 | 8.66 ± 0.79 | 9.95 ± 0.79 |
| HMM-src | 7.45 ± 2.16 | 10.38 ± 0.70 | 16.94 ± 1.21 | 9.33 ± 0.91 | 10.23 ± 0.91 |
| HMM-src[rawE] | 6.79 ± 0.83 | 9.20 ± 0.40 | 15.76 ± 1.58 | 6.06 ± 0.66 | 7.39 ± 0.71 |
| HMM-src[sel] (post hoc R1) | 10.95 ± nan | 11.21 ± nan | 17.75 ± nan | 10.03 ± nan | 10.96 ± nan |
| PA-HMMQ (pre-registered) | 7.40 ± 1.78 | 10.59 ± 0.64 | 17.50 ± 1.06 | 9.53 ± 0.94 | 10.47 ± 0.91 |
| PA-HMMQ (final) | 6.86 ± 0.62 | 9.26 ± 0.39 | 15.87 ± 1.41 | 6.10 ± 0.65 | 7.44 ± 0.69 |
| PA-HMMQ[sel] (post hoc R1) | 10.21 ± nan | 11.28 ± nan | 17.79 ± nan | 10.15 ± nan | 11.07 ± nan |

Mean ± SD over seeds.

**Table S4 Per-patient AF-burden MAE (pp) by estimator, RRNet detector**

| Estimator | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|
| CC | 3.55 ± 1.29 | 4.78 ± 0.46 | 5.01 ± 1.15 | 3.72 ± 0.88 | 3.96 ± 0.83 |
| CC-MF | 3.34 ± 1.20 | 4.52 ± 0.40 | 4.73 ± 1.21 | 3.50 ± 0.84 | 3.72 ± 0.80 |
| PCC | 4.02 ± 1.16 | 5.06 ± 0.50 | 5.86 ± 1.35 | 4.10 ± 0.99 | 4.37 ± 0.93 |
| PCC-iso | 3.67 ± 0.82 | 5.00 ± 0.33 | 5.50 ± 0.99 | 3.96 ± 0.67 | 4.22 ± 0.63 |
| ACC | 3.54 ± 1.21 | 4.97 ± 0.44 | 4.81 ± 1.26 | 3.59 ± 0.84 | 3.85 ± 0.81 |
| PACC | 3.71 ± 1.09 | 5.18 ± 0.51 | 5.27 ± 1.39 | 3.82 ± 0.92 | 4.10 ± 0.89 |
| EMQ | 3.03 ± 0.97 | 4.85 ± 0.44 | 4.51 ± 1.15 | 3.37 ± 0.64 | 3.63 ± 0.61 |
| HMM-src | 2.64 ± 1.06 | 4.55 ± 0.41 | 4.49 ± 1.01 | 3.53 ± 0.68 | 3.73 ± 0.64 |
| HMM-src[rawE] | 3.00 ± 1.12 | 4.29 ± 0.26 | 4.21 ± 1.14 | 3.22 ± 0.75 | 3.43 ± 0.70 |
| HMM-src[sel] (post hoc R1) | nan ± nan | nan ± nan | nan ± nan | nan ± nan | nan ± nan |
| PA-HMMQ (pre-registered) | 2.68 ± 1.06 | 4.60 ± 0.44 | 4.59 ± 0.95 | 3.57 ± 0.70 | 3.78 ± 0.65 |
| PA-HMMQ (final) | 3.18 ± 1.08 | 4.31 ± 0.28 | 4.20 ± 1.06 | 3.25 ± 0.76 | 3.45 ± 0.70 |
| PA-HMMQ[sel] (post hoc R1) | nan ± nan | nan ± nan | nan ± nan | nan ± nan | nan ± nan |

Mean ± SD over seeds.

**Table S5 Ablation of PA-HMMQ components (LightGBM, MAE in pp)**

| Variant | Calibration B | Development test | SHDB-AF | CPSC2021 | Icentia11k | Pooled external |
|---|---|---|---|---|---|---|
| PA-HMMQ | 3.40 ± 1.79 | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.50 ± 1.06 | 2.84 ± 0.34 | 3.07 ± 0.30 |
| PA-HMMQ[k=0] | 3.35 ± 1.84 | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.54 ± 1.09 | 2.84 ± 0.34 | 3.08 ± 0.31 |
| PA-HMMQ[k=100] | 3.49 ± 1.76 | 2.98 ± 1.03 | 4.54 ± 0.36 | 3.47 ± 1.03 | 2.83 ± 0.33 | 3.06 ± 0.29 |
| PA-HMMQ[k=1] | 3.37 ± 1.81 | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.54 ± 1.08 | 2.84 ± 0.34 | 3.08 ± 0.31 |
| PA-HMMQ[k=30] | 3.46 ± 1.75 | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.48 ± 1.05 | 2.84 ± 0.34 | 3.07 ± 0.30 |
| PA-HMMQ[k=3] | 3.38 ± 1.80 | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.52 ± 1.07 | 2.84 ± 0.34 | 3.08 ± 0.31 |
| PA-HMMQ[rawE,k=0] | 2.68 ± 1.56 | 3.04 ± 1.26 | 4.23 ± 0.11 | 2.77 ± 0.38 | 2.27 ± 0.33 | 2.51 ± 0.25 |
| PA-HMMQ[rawE,k=100] | 2.76 ± 1.53 | 3.03 ± 1.28 | 4.24 ± 0.11 | 2.98 ± 0.45 | 2.26 ± 0.33 | 2.52 ± 0.23 |
| PA-HMMQ[rawE,k=1] | 2.66 ± 1.55 | 3.04 ± 1.25 | 4.23 ± 0.11 | 2.80 ± 0.38 | 2.27 ± 0.33 | 2.51 ± 0.25 |
| PA-HMMQ[rawE,k=30] | 2.71 ± 1.54 | 3.03 ± 1.26 | 4.24 ± 0.11 | 2.94 ± 0.42 | 2.26 ± 0.33 | 2.52 ± 0.24 |
| PA-HMMQ[rawE,k=3] | 2.66 ± 1.57 | 3.04 ± 1.25 | 4.23 ± 0.11 | 2.84 ± 0.38 | 2.27 ± 0.33 | 2.51 ± 0.25 |
| PA-HMMQ[rawE] | 2.67 ± 1.57 | 3.04 ± 1.26 | 4.23 ± 0.11 | 2.88 ± 0.39 | 2.27 ± 0.33 | 2.52 ± 0.24 |
| PA-HMMQ[sel] | 1.07 ± nan | 1.96 ± nan | 4.40 ± nan | 3.69 ± nan | 2.42 ± nan | 2.74 ± nan |
| CC | 2.86 ± 1.25 | 3.55 ± 1.05 | 4.51 ± 0.12 | 3.85 ± 0.76 | 2.69 ± 0.35 | 2.99 ± 0.26 |
| EMQ | 3.48 ± 1.74 | 3.10 ± 0.93 | 4.92 ± 0.52 | 3.78 ± 1.12 | 2.72 ± 0.29 | 3.04 ± 0.21 |
| HMM-src | 3.56 ± 1.84 | 3.00 ± 1.02 | 4.53 ± 0.37 | 3.48 ± 1.02 | 2.82 ± 0.33 | 3.05 ± 0.29 |
| HMM-src[rawE] | 2.84 ± 1.54 | 3.04 ± 1.32 | 4.24 ± 0.10 | 3.02 ± 0.43 | 2.25 ± 0.31 | 2.52 ± 0.22 |
| HMM-src[sel] | 1.03 ± nan | 1.69 ± nan | 4.38 ± nan | 3.56 ± nan | 2.33 ± nan | 2.65 ± nan |

k, prior strength κ in pseudo-transitions (κ=10 pre-specified); rawE, detector probability used as emission likelihood (final variant); HMM-src, no per-patient adaptation (κ→∞); EMQ, per-patient prior adaptation without temporal model; CC, no quantification.

**Table S6 MAE (pp) by reference burden stratum, pooled external cohorts (LightGBM)**

| Estimator | 0 (AF-free) (n=813) | (0,1%] (n=16) | (1,10%] (n=30) | (10,50%] (n=35) | >50% (n=94) |
|---|---|---|---|---|---|
| CC | 2.66 | 5.81 | 1.84 | 4.72 | 5.02 |
| CC-MF | 2.45 | 5.65 | 1.60 | 4.58 | 4.37 |
| PCC-iso | 3.47 | 6.89 | 3.31 | 5.66 | 6.08 |
| ACC | 2.59 | 5.88 | 2.06 | 5.10 | 4.45 |
| EMQ | 2.77 | 6.01 | 2.32 | 7.56 | 3.46 |
| HMM-src | 2.89 | 5.88 | 2.78 | 6.14 | 2.93 |
| HMM-src[rawE] | 2.22 | 5.62 | 1.53 | 4.54 | 4.16 |
| PA-HMMQ (pre-registered) | 2.91 | 5.95 | 2.77 | 6.18 | 2.90 |
| PA-HMMQ (final) | 2.24 | 5.62 | 1.56 | 4.44 | 4.00 |
| PA-HMMQ[sel] | 2.50 | 5.93 | 1.92 | 5.33 | 3.58 |

Mean over seeds.

**Table S7 Classification of patients by burden thresholds, pooled external cohorts (LightGBM)**

| Estimator | present_30s sens | present_30s spec | ge1pct sens | ge1pct spec | ge10pct sens | ge10pct spec |
|---|---|---|---|---|---|---|
| CC | 0.992 ± 0.003 | 0.744 ± 0.034 | 0.992 ± 0.005 | 0.850 ± 0.026 | 0.974 ± 0.004 | 0.946 ± 0.011 |
| CC-MF | 0.982 ± 0.005 | 0.826 ± 0.027 | 0.989 ± 0.007 | 0.882 ± 0.022 | 0.974 ± 0.004 | 0.954 ± 0.010 |
| PCC-iso | 0.997 ± 0.003 | 0.487 ± 0.251 | 1.000 ± 0.000 | 0.712 ± 0.136 | 0.977 ± 0.000 | 0.923 ± 0.011 |
| ACC | 0.949 ± 0.028 | 0.846 ± 0.027 | 0.979 ± 0.008 | 0.879 ± 0.016 | 0.972 ± 0.004 | 0.948 ± 0.009 |
| EMQ | 0.961 ± 0.018 | 0.895 ± 0.025 | 0.976 ± 0.010 | 0.911 ± 0.020 | 0.975 ± 0.003 | 0.949 ± 0.006 |
| HMM-src | 0.971 ± 0.004 | 0.869 ± 0.018 | 0.987 ± 0.004 | 0.891 ± 0.019 | 0.978 ± 0.003 | 0.943 ± 0.009 |
| HMM-src[rawE] | 0.947 ± 0.014 | 0.910 ± 0.025 | 0.967 ± 0.011 | 0.925 ± 0.020 | 0.971 ± 0.003 | 0.961 ± 0.008 |
| PA-HMMQ (pre-registered) | 0.965 ± 0.008 | 0.877 ± 0.022 | 0.985 ± 0.006 | 0.889 ± 0.017 | 0.978 ± 0.003 | 0.940 ± 0.009 |
| PA-HMMQ (final) | 0.941 ± 0.014 | 0.914 ± 0.025 | 0.971 ± 0.012 | 0.923 ± 0.021 | 0.974 ± 0.004 | 0.960 ± 0.009 |
| PA-HMMQ[sel] | 0.971 ± nan | 0.866 ± nan | 0.994 ± nan | 0.887 ± nan | 0.977 ± nan | 0.950 ± nan |

present_30s: ≥30 s of AF in the analysed recording; ge1pct/ge10pct: burden ≥1%/≥10%. Mean ± SD over seeds.

**Table S8 Influence of atrial flutter (LightGBM, pooled external)**

| Estimator | MAE vs AF reference (pp) | MAE vs AF+AFL reference (pp) | MAE excluding patients with any AFL, n=949 (post hoc) |
|---|---|---|---|
| CC | 2.99 ± 0.26 | 2.11 ± 0.22 | 1.67 ± 0.25 |
| CC-MF | 2.73 ± 0.23 | 1.85 ± 0.20 | 1.41 ± 0.23 |
| PCC | 3.94 ± 0.57 | 3.10 ± 0.67 | 2.67 ± 0.63 |
| PCC-iso | 3.85 ± 0.51 | 2.95 ± 0.57 | 2.55 ± 0.55 |
| ACC | 2.89 ± 0.22 | 1.98 ± 0.19 | 1.55 ± 0.21 |
| PACC | 3.21 ± 0.15 | 2.29 ± 0.17 | 1.87 ± 0.16 |
| EMQ | 3.04 ± 0.21 | 2.03 ± 0.20 | 1.66 ± 0.21 |
| HMM-src | 3.05 ± 0.29 | 2.02 ± 0.26 | 1.67 ± 0.28 |
| HMM-src[rawE] | 2.52 ± 0.22 | 1.65 ± 0.19 | 1.19 ± 0.22 |
| PA-HMMQ (pre-registered) | 3.07 ± 0.30 | 2.03 ± 0.27 | 1.69 ± 0.29 |
| PA-HMMQ (final) | 2.52 ± 0.24 | 1.64 ± 0.21 | 1.19 ± 0.23 |
| PA-HMMQ[sel] | 2.74 ± nan | 1.81 ± nan | 1.40 ± nan |

The AF+AFL reference counts flutter time as arrhythmia time. The analysis excluding patients with any flutter is post hoc.

**Table S11 Sensitivity to training-set size and window length (LightGBM, MAE in pp)**

| Setting | Estimator | Development test | SHDB-AF | CPSC2021 |
|---|---|---|---|---|
| 100% training data, W=60 (main) | CC | 3.55 ± 1.05 | 4.51 ± 0.12 | 3.85 ± 0.76 |
| 100% training data, W=60 (main) | CC-MF | 3.24 ± 1.22 | 4.31 ± 0.11 | 3.38 ± 0.67 |
| 100% training data, W=60 (main) | PCC-iso | 4.16 ± 0.92 | 5.13 ± 0.42 | 5.50 ± 1.38 |
| 100% training data, W=60 (main) | ACC | 3.49 ± 1.03 | 4.73 ± 0.31 | 3.53 ± 0.71 |
| 100% training data, W=60 (main) | EMQ | 3.10 ± 0.93 | 4.92 ± 0.52 | 3.78 ± 1.12 |
| 100% training data, W=60 (main) | HMM-src | 3.00 ± 1.02 | 4.53 ± 0.37 | 3.48 ± 1.02 |
| 100% training data, W=60 (main) | PA-HMMQ (pre-registered) | 2.97 ± 1.03 | 4.54 ± 0.36 | 3.50 ± 1.06 |
| 100% training data, W=60 (main) | PA-HMMQ (final) | 3.04 ± 1.26 | 4.23 ± 0.11 | 2.88 ± 0.39 |
| 25% training data | CC | 3.45 ± 0.49 | 4.89 ± 0.16 | 4.02 ± 0.36 |
| 25% training data | CC-MF | 2.99 ± 0.53 | 4.67 ± 0.16 | 3.46 ± 0.31 |
| 25% training data | PCC-iso | 4.20 ± 0.82 | 5.36 ± 0.51 | 5.17 ± 0.91 |
| 25% training data | ACC | 3.32 ± 0.45 | 5.12 ± 0.26 | 3.69 ± 0.41 |
| 25% training data | EMQ | 2.88 ± 0.74 | 5.03 ± 0.38 | 3.23 ± 0.47 |
| 25% training data | HMM-src | 2.48 ± 0.82 | 4.65 ± 0.10 | 3.17 ± 0.41 |
| 25% training data | PA-HMMQ (pre-registered) | 2.56 ± 0.80 | 4.67 ± 0.09 | 3.24 ± 0.50 |
| 25% training data | PA-HMMQ (final) | 2.71 ± 0.73 | 4.54 ± 0.15 | 2.92 ± 0.24 |
| 50% training data | CC | 3.80 ± 1.40 | 4.89 ± 0.28 | 3.78 ± 0.43 |
| 50% training data | CC-MF | 3.42 ± 1.53 | 4.66 ± 0.20 | 3.23 ± 0.37 |
| 50% training data | PCC-iso | 4.44 ± 1.11 | 5.48 ± 0.53 | 5.52 ± 1.33 |
| 50% training data | ACC | 3.66 ± 1.34 | 5.13 ± 0.38 | 3.37 ± 0.43 |
| 50% training data | EMQ | 3.02 ± 0.84 | 5.18 ± 0.50 | 3.38 ± 0.45 |
| 50% training data | HMM-src | 2.91 ± 0.96 | 4.71 ± 0.09 | 3.24 ± 0.39 |
| 50% training data | PA-HMMQ (pre-registered) | 2.96 ± 1.03 | 4.73 ± 0.09 | 3.30 ± 0.48 |
| 50% training data | PA-HMMQ (final) | 3.18 ± 1.62 | 4.56 ± 0.16 | 2.70 ± 0.25 |
| window = 30 beats | CC | 3.69 ± 1.49 | 5.13 ± 0.23 | 5.51 ± 0.80 |
| window = 30 beats | CC-MF | 3.19 ± 1.66 | 4.76 ± 0.24 | 4.39 ± 0.75 |
| window = 30 beats | PCC-iso | 5.15 ± 1.57 | 6.04 ± 0.65 | 7.80 ± 1.57 |
| window = 30 beats | ACC | 3.52 ± 1.49 | 5.33 ± 0.31 | 4.90 ± 0.80 |
| window = 30 beats | EMQ | 3.39 ± 0.92 | 5.55 ± 0.50 | 5.14 ± 1.26 |
| window = 30 beats | HMM-src | 3.07 ± 0.97 | 4.99 ± 0.37 | 4.68 ± 0.94 |
| window = 30 beats | PA-HMMQ (pre-registered) | 3.01 ± 0.99 | 5.01 ± 0.35 | 4.87 ± 0.91 |
| window = 30 beats | PA-HMMQ (final) | 2.86 ± 1.93 | 4.49 ± 0.19 | 3.25 ± 0.55 |
| window = 120 beats | CC | 3.31 ± 1.62 | 4.59 ± 0.22 | 4.28 ± 0.58 |
| window = 120 beats | CC-MF | 3.14 ± 1.52 | 4.53 ± 0.21 | 4.00 ± 0.41 |
| window = 120 beats | PCC-iso | 4.03 ± 0.61 | 5.27 ± 1.02 | 5.93 ± 1.69 |
| window = 120 beats | ACC | 3.39 ± 1.59 | 4.99 ± 0.09 | 4.11 ± 0.45 |
| window = 120 beats | EMQ | 3.04 ± 1.19 | 5.09 ± 1.00 | 3.97 ± 1.41 |
| window = 120 beats | HMM-src | 3.03 ± 1.23 | 4.49 ± 0.23 | 3.99 ± 0.64 |
| window = 120 beats | PA-HMMQ (pre-registered) | 3.07 ± 1.28 | 4.51 ± 0.20 | 4.05 ± 0.73 |
| window = 120 beats | PA-HMMQ (final) | 2.94 ± 1.25 | 4.50 ± 0.15 | 3.53 ± 0.26 |

Reduced-data and window-length runs used SHDB-AF and CPSC2021 as external cohorts (Icentia11k omitted for computational reasons).

**Table S12 Subgroup MAE (pp) in SHDB-AF by sex and age (LightGBM)**

| Estimator | Subgroup | n | MAE (pp) |
|---|---|---|---|
| CC | female | 42 | 3.78 |
| CC | male | 51 | 5.12 |
| CC | age < 69 | 45 | 1.91 |
| CC | age ≥ 69 | 48 | 6.96 |
| PA-HMMQ (pre-registered) | female | 42 | 3.30 |
| PA-HMMQ (pre-registered) | male | 51 | 5.57 |
| PA-HMMQ (pre-registered) | age < 69 | 45 | 1.68 |
| PA-HMMQ (pre-registered) | age ≥ 69 | 48 | 7.23 |
| PA-HMMQ (final) | female | 42 | 3.63 |
| PA-HMMQ (final) | male | 51 | 4.73 |
| PA-HMMQ (final) | age < 69 | 45 | 1.73 |
| PA-HMMQ (final) | age ≥ 69 | 48 | 6.58 |

Age split at the cohort median.

**Table S13 The 15 external patients with the largest absolute error of the final PA-HMMQ (LightGBM, seed-averaged)**

| patient | ae | err | true_burden | ectopy_sv | ectopy_v | afl | hours | db |
|---|---|---|---|---|---|---|---|---|
| icentia_p05828 | 100.000 | 100.000 | 0.000 | 0.000 | 0.000 | 1.000 | 5.274 | icentia11k |
| icentia_p01292 | 100.000 | 100.000 | 0.000 | 0.000 | 0.017 | 1.000 | 6.351 | icentia11k |
| icentia_p01304 | 100.000 | 100.000 | 0.000 | 0.000 | 0.031 | 1.000 | 1.236 | icentia11k |
| icentia_p05149 | 100.000 | 100.000 | 0.000 | 0.000 | 0.023 | 1.000 | 8.921 | icentia11k |
| icentia_p07973 | 99.991 | 99.991 | 0.000 | 0.000 | 0.000 | 1.000 | 5.662 | icentia11k |
| icentia_p00921 | 97.229 | 97.229 | 0.000 | 0.000 | 0.162 | 1.000 | 2.271 | icentia11k |
| icentia_p09800 | 91.539 | 91.539 | 0.000 | 0.000 | 0.000 | 1.000 | 10.668 | icentia11k |
| icentia_p06999 | 87.350 | 87.350 | 0.000 | 0.417 | 0.006 | 0.000 | 7.884 | icentia11k |
| cpsc_II_54 | 87.160 | -87.160 | 1.000 | 0.000 | 0.001 | 0.000 | 0.708 | cpsc2021 |
| icentia_p08389 | 85.769 | 85.769 | 0.000 | 0.000 | 0.001 | 0.858 | 6.546 | icentia11k |
| icentia_p10993 | 80.605 | 80.605 | 0.000 | 0.000 | 0.000 | 0.806 | 7.194 | icentia11k |
| icentia_p03332 | 78.338 | 78.338 | 0.000 | 0.000 | 0.000 | 1.000 | 7.721 | icentia11k |
| icentia_p06217 | 70.810 | 70.810 | 0.000 | 0.016 | 0.003 | 0.708 | 7.050 | icentia11k |
| shdb_2148042 | 70.431 | -70.431 | 1.000 | 0.000 | 0.000 | 0.000 | 23.816 | shdb-af |
| shdb_5210865 | 69.129 | 69.129 | 0.000 | 0.000 | 0.000 | 0.723 | 23.996 | shdb-af |

ae, absolute error (pp); err, signed error (pp); true_burden, fraction; ectopy and AFL as fractions of beats/time.

**Table S14 All paired comparisons (all detectors, cohorts and both PA-HMMQ variants)**

| Detector | Proposed | Cohort | Comparator | n patients | Mean AE proposed (pp) | Mean AE comparator (pp) | Mean paired diff (pp) [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Classical-LR | PA-HMMQ (final) | Pooled external | CC | 988 | 7.44 | 8.54 | -1.10 [-1.31, -0.92] | 7.6e-36 |
| Classical-LR | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 7.44 | 8.14 | -0.71 [-0.85, -0.57] | 8.8e-06 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PCC | 988 | 7.44 | 13.90 | -6.46 [-6.88, -6.03] | 7.7e-119 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 7.44 | 11.70 | -4.26 [-4.70, -3.85] | 5e-103 |
| Classical-LR | PA-HMMQ (final) | Pooled external | ACC | 988 | 7.44 | 8.40 | -0.96 [-1.15, -0.77] | 0.0002 |
| Classical-LR | PA-HMMQ (final) | Pooled external | PACC | 988 | 7.44 | 10.37 | -2.93 [-3.27, -2.59] | 4.8e-54 |
| Classical-LR | PA-HMMQ (final) | Pooled external | EMQ | 988 | 7.44 | 9.95 | -2.51 [-3.08, -1.99] | 0.086 |
| Classical-LR | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 7.44 | 10.23 | -2.80 [-3.37, -2.23] | 1.9e-86 |
| Classical-LR | PA-HMMQ (final) | Pooled external | HMM-src[rawE] (post hoc, same emissions) | 988 | 7.44 | 7.39 | 0.05 [0.00, 0.10] | 1.2e-30 |
| Classical-LR | PA-HMMQ (final) | Development test | CC | 160 | 7.82 | 8.46 | -0.64 [-1.18, -0.04] | 0.0047 |
| Classical-LR | PA-HMMQ (final) | Development test | CC-MF | 160 | 7.82 | 8.17 | -0.35 [-0.72, 0.02] | 0.18 |
| Classical-LR | PA-HMMQ (final) | Development test | PCC | 160 | 7.82 | 13.80 | -5.98 [-7.24, -4.66] | 2e-15 |
| Classical-LR | PA-HMMQ (final) | Development test | PCC-iso | 160 | 7.82 | 11.40 | -3.58 [-4.85, -2.37] | 1e-11 |
| Classical-LR | PA-HMMQ (final) | Development test | ACC | 160 | 7.82 | 8.27 | -0.45 [-0.94, 0.03] | 1 |
| Classical-LR | PA-HMMQ (final) | Development test | PACC | 160 | 7.82 | 9.86 | -2.04 [-3.00, -1.04] | 0.0047 |
| Classical-LR | PA-HMMQ (final) | Development test | EMQ | 160 | 7.82 | 8.32 | -0.50 [-2.17, 1.14] | 1 |
| Classical-LR | PA-HMMQ (final) | Development test | HMM-src | 160 | 7.82 | 8.37 | -0.55 [-2.64, 1.38] | 0.02 |
| Classical-LR | PA-HMMQ (final) | Development test | HMM-src[rawE] (post hoc, same emissions) | 160 | 7.82 | 7.71 | 0.11 [-0.15, 0.47] | 0.0065 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | CC | 93 | 9.26 | 9.94 | -0.68 [-1.14, -0.23] | 0.00049 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 9.26 | 9.69 | -0.43 [-0.73, -0.13] | 0.016 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 9.26 | 12.31 | -3.05 [-4.08, -1.92] | 1.6e-07 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 9.26 | 11.13 | -1.87 [-2.91, -0.81] | 1.8e-05 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 9.26 | 11.01 | -1.75 [-2.43, -1.06] | 6.9e-05 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 9.26 | 12.16 | -2.90 [-3.82, -1.96] | 3.2e-07 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 9.26 | 11.42 | -2.16 [-3.16, -1.18] | 1.1e-05 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 9.26 | 10.38 | -1.12 [-2.13, -0.05] | 0.0023 |
| Classical-LR | PA-HMMQ (final) | SHDB-AF | HMM-src[rawE] (post hoc, same emissions) | 93 | 9.26 | 9.20 | 0.06 [-0.01, 0.13] | 0.38 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | CC | 105 | 15.87 | 17.34 | -1.47 [-2.38, -0.63] | 0.003 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 15.87 | 16.95 | -1.08 [-1.83, -0.41] | 0.091 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 15.87 | 22.10 | -6.23 [-7.91, -4.53] | 1e-08 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 15.87 | 20.82 | -4.95 [-6.57, -3.29] | 7.9e-07 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 15.87 | 17.75 | -1.88 [-2.89, -0.90] | 0.079 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 15.87 | 20.05 | -4.18 [-5.51, -2.81] | 2e-06 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 15.87 | 18.32 | -2.45 [-4.63, -0.11] | 0.091 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 15.87 | 16.94 | -1.07 [-3.46, 1.39] | 0.0078 |
| Classical-LR | PA-HMMQ (final) | CPSC2021 | HMM-src[rawE] (post hoc, same emissions) | 105 | 15.87 | 15.76 | 0.10 [-0.34, 0.51] | 0.67 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | CC | 790 | 6.10 | 7.20 | -1.10 [-1.32, -0.89] | 1.5e-28 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 6.10 | 6.79 | -0.69 [-0.85, -0.55] | 0.00066 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PCC | 790 | 6.10 | 12.99 | -6.89 [-7.32, -6.44] | 1.6e-104 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 6.10 | 10.55 | -4.45 [-4.92, -3.98] | 3.6e-97 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | ACC | 790 | 6.10 | 6.84 | -0.74 [-0.93, -0.57] | 1.5e-14 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | PACC | 790 | 6.10 | 8.87 | -2.76 [-3.15, -2.41] | 7.5e-42 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 6.10 | 8.66 | -2.56 [-3.16, -2.01] | 8.6e-08 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 6.10 | 9.33 | -3.22 [-3.87, -2.65] | 9.2e-93 |
| Classical-LR | PA-HMMQ (final) | Icentia11k | HMM-src[rawE] (post hoc, same emissions) | 790 | 6.10 | 6.06 | 0.04 [0.01, 0.07] | 1.3e-42 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 10.47 | 8.54 | 1.93 [1.43, 2.44] | 5.8e-13 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 10.47 | 8.14 | 2.33 [1.82, 2.85] | 9.5e-55 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 10.47 | 13.90 | -3.42 [-3.99, -2.82] | 1.8e-50 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 10.47 | 11.70 | -1.23 [-1.67, -0.77] | 7e-35 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 10.47 | 8.40 | 2.08 [1.59, 2.57] | 1.3e-68 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 10.47 | 10.37 | 0.11 [-0.31, 0.51] | 0.91 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 10.47 | 9.95 | 0.52 [0.27, 0.75] | 4.1e-50 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 10.47 | 10.23 | 0.24 [0.18, 0.31] | 0.04 |
| Classical-LR | PA-HMMQ (pre-registered) | Pooled external | HMM-src (post hoc, same emissions) | 988 | 10.47 | 10.23 | 0.24 [0.18, 0.31] | 0.02 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | CC | 160 | 8.26 | 8.46 | -0.20 [-2.03, 1.86] | 0.85 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | CC-MF | 160 | 8.26 | 8.17 | 0.08 [-1.77, 2.07] | 0.71 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PCC | 160 | 8.26 | 13.80 | -5.55 [-7.46, -3.55] | 1.4e-12 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PCC-iso | 160 | 8.26 | 11.40 | -3.15 [-4.77, -1.50] | 8.8e-10 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | ACC | 160 | 8.26 | 8.27 | -0.01 [-1.75, 1.91] | 0.71 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | PACC | 160 | 8.26 | 9.86 | -1.60 [-3.08, 0.02] | 0.12 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | EMQ | 160 | 8.26 | 8.32 | -0.06 [-0.85, 0.64] | 0.32 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | HMM-src | 160 | 8.26 | 8.37 | -0.11 [-0.41, 0.14] | 0.34 |
| Classical-LR | PA-HMMQ (pre-registered) | Development test | HMM-src (post hoc, same emissions) | 160 | 8.26 | 8.37 | -0.11 [-0.41, 0.14] | 0.084 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 10.59 | 9.94 | 0.65 [-0.27, 1.51] | 0.31 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 10.59 | 9.69 | 0.90 [-0.04, 1.79] | 0.024 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 10.59 | 12.31 | -1.72 [-3.01, -0.42] | 0.0032 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 10.59 | 11.13 | -0.54 [-1.70, 0.63] | 0.087 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 10.59 | 11.01 | -0.42 [-1.37, 0.48] | 0.56 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 10.59 | 12.16 | -1.57 [-2.54, -0.60] | 0.026 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 10.59 | 11.42 | -0.84 [-1.54, -0.12] | 0.17 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 10.59 | 10.38 | 0.21 [0.09, 0.34] | 0.09 |
| Classical-LR | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src (post hoc, same emissions) | 93 | 10.59 | 10.38 | 0.21 [0.09, 0.34] | 0.023 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 17.50 | 17.34 | 0.16 [-2.09, 2.53] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 17.50 | 16.95 | 0.54 [-1.70, 2.91] | 0.25 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 17.50 | 22.10 | -4.61 [-7.23, -1.82] | 0.017 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 17.50 | 20.82 | -3.32 [-5.44, -1.05] | 0.037 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 17.50 | 17.75 | -0.26 [-2.36, 1.80] | 0.25 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 17.50 | 20.05 | -2.55 [-4.59, -0.58] | 0.76 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 17.50 | 18.32 | -0.83 [-2.03, 0.30] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 17.50 | 16.94 | 0.56 [0.19, 0.97] | 1 |
| Classical-LR | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src (post hoc, same emissions) | 105 | 17.50 | 16.94 | 0.56 [0.19, 0.97] | 0.79 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 9.53 | 7.20 | 2.32 [1.82, 2.84] | 1.1e-15 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 9.53 | 6.79 | 2.73 [2.22, 3.27] | 2.2e-59 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 9.53 | 12.99 | -3.47 [-4.11, -2.89] | 3.5e-48 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 9.53 | 10.55 | -1.03 [-1.50, -0.60] | 8e-36 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 9.53 | 6.84 | 2.68 [2.19, 3.23] | 1.1e-87 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 9.53 | 8.87 | 0.66 [0.28, 1.05] | 0.17 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 9.53 | 8.66 | 0.86 [0.63, 1.08] | 5.8e-72 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 9.53 | 9.33 | 0.20 [0.15, 0.26] | 0.00064 |
| Classical-LR | PA-HMMQ (pre-registered) | Icentia11k | HMM-src (post hoc, same emissions) | 790 | 9.53 | 9.33 | 0.20 [0.15, 0.26] | 0.00032 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | CC | 988 | 11.07 | 8.54 | 2.53 [1.87, 3.18] | 1.3e-14 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | CC-MF | 988 | 11.07 | 8.14 | 2.92 [2.25, 3.60] | 1.9e-54 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | PCC | 988 | 11.07 | 13.90 | -2.83 [-3.53, -2.09] | 1.5e-38 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | PCC-iso | 988 | 11.07 | 11.70 | -0.63 [-1.20, -0.05] | 1.5e-22 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | ACC | 988 | 11.07 | 8.40 | 2.67 [2.01, 3.31] | 4.2e-74 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | PACC | 988 | 11.07 | 10.37 | 0.70 [0.10, 1.26] | 0.056 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | EMQ | 988 | 11.07 | 9.95 | 1.11 [0.70, 1.51] | 1.9e-72 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | HMM-src | 988 | 11.07 | 10.23 | 0.83 [0.59, 1.08] | 0.17 |
| Classical-LR | PA-HMMQ[sel] | Pooled external | HMM-src[sel] (post hoc, same emissions) | 988 | 11.07 | 10.96 | 0.11 [0.04, 0.17] | 1.6e-15 |
| Classical-LR | PA-HMMQ[sel] | Development test | CC | 49 | 10.21 | 8.71 | 1.50 [-3.30, 7.10] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | CC-MF | 49 | 10.21 | 8.21 | 2.00 [-2.71, 7.69] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | PCC | 49 | 10.21 | 14.97 | -4.76 [-9.41, -0.13] | 0.00097 |
| Classical-LR | PA-HMMQ[sel] | Development test | PCC-iso | 49 | 10.21 | 12.99 | -2.78 [-6.70, 1.31] | 0.01 |
| Classical-LR | PA-HMMQ[sel] | Development test | ACC | 49 | 10.21 | 8.68 | 1.53 [-3.05, 7.17] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | PACC | 49 | 10.21 | 11.64 | -1.42 [-5.59, 2.90] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | EMQ | 49 | 10.21 | 10.74 | -0.53 [-2.68, 1.15] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | HMM-src | 49 | 10.21 | 10.91 | -0.70 [-1.79, 0.19] | 1 |
| Classical-LR | PA-HMMQ[sel] | Development test | HMM-src[sel] (post hoc, same emissions) | 49 | 10.21 | 10.95 | -0.74 [-1.63, -0.05] | 0.089 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | CC | 93 | 11.28 | 9.94 | 1.34 [0.00, 2.70] | 0.25 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | CC-MF | 93 | 11.28 | 9.69 | 1.59 [0.21, 2.99] | 0.017 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | PCC | 93 | 11.28 | 12.31 | -1.03 [-2.65, 0.60] | 0.079 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | PCC-iso | 93 | 11.28 | 11.13 | 0.15 [-1.31, 1.57] | 0.84 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | ACC | 93 | 11.28 | 11.01 | 0.27 [-1.13, 1.56] | 0.84 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | PACC | 93 | 11.28 | 12.16 | -0.88 [-2.26, 0.48] | 0.84 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | EMQ | 93 | 11.28 | 11.42 | -0.14 [-1.36, 1.01] | 0.85 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | HMM-src | 93 | 11.28 | 10.38 | 0.91 [0.15, 1.66] | 0.005 |
| Classical-LR | PA-HMMQ[sel] | SHDB-AF | HMM-src[sel] (post hoc, same emissions) | 93 | 11.28 | 11.21 | 0.07 [-0.06, 0.22] | 0.83 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | CC | 105 | 17.79 | 17.34 | 0.45 [-2.55, 3.49] | 0.81 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | CC-MF | 105 | 17.79 | 16.95 | 0.84 [-2.24, 3.84] | 0.12 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | PCC | 105 | 17.79 | 22.10 | -4.31 [-7.54, -0.86] | 0.12 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | PCC-iso | 105 | 17.79 | 20.82 | -3.03 [-5.85, -0.19] | 0.15 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | ACC | 105 | 17.79 | 17.75 | 0.04 [-2.87, 2.86] | 0.091 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | PACC | 105 | 17.79 | 20.05 | -2.26 [-5.21, 0.55] | 0.81 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | EMQ | 105 | 17.79 | 18.32 | -0.53 [-2.70, 1.36] | 0.016 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | HMM-src | 105 | 17.79 | 16.94 | 0.85 [-0.22, 1.81] | 0.31 |
| Classical-LR | PA-HMMQ[sel] | CPSC2021 | HMM-src[sel] (post hoc, same emissions) | 105 | 17.79 | 17.75 | 0.04 [-0.27, 0.35] | 0.13 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | CC | 790 | 10.15 | 7.20 | 2.94 [2.26, 3.62] | 2.3e-16 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | CC-MF | 790 | 10.15 | 6.79 | 3.35 [2.67, 4.06] | 1.4e-57 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | PCC | 790 | 10.15 | 12.99 | -2.84 [-3.60, -2.14] | 8.7e-39 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | PCC-iso | 790 | 10.15 | 10.55 | -0.41 [-1.01, 0.14] | 3.4e-24 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | ACC | 790 | 10.15 | 6.84 | 3.30 [2.65, 4.02] | 5.3e-89 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | PACC | 790 | 10.15 | 8.87 | 1.28 [0.71, 1.84] | 0.014 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | EMQ | 790 | 10.15 | 8.66 | 1.48 [1.07, 1.88] | 3.5e-89 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | HMM-src | 790 | 10.15 | 9.33 | 0.82 [0.56, 1.09] | 0.46 |
| Classical-LR | PA-HMMQ[sel] | Icentia11k | HMM-src[sel] (post hoc, same emissions) | 790 | 10.15 | 10.03 | 0.12 [0.06, 0.19] | 5.2e-18 |
| LightGBM | PA-HMMQ (final) | Pooled external | CC | 988 | 2.52 | 2.99 | -0.47 [-0.56, -0.38] | 1e-08 |
| LightGBM | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 2.52 | 2.73 | -0.21 [-0.27, -0.17] | 0.23 |
| LightGBM | PA-HMMQ (final) | Pooled external | PCC | 988 | 2.52 | 3.94 | -1.42 [-1.57, -1.28] | 2.4e-128 |
| LightGBM | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 2.52 | 3.85 | -1.33 [-1.50, -1.16] | 2.2e-125 |
| LightGBM | PA-HMMQ (final) | Pooled external | ACC | 988 | 2.52 | 2.89 | -0.37 [-0.46, -0.30] | 0.23 |
| LightGBM | PA-HMMQ (final) | Pooled external | PACC | 988 | 2.52 | 3.21 | -0.69 [-0.83, -0.57] | 0.2 |
| LightGBM | PA-HMMQ (final) | Pooled external | EMQ | 988 | 2.52 | 3.04 | -0.53 [-0.74, -0.33] | 3.6e-21 |
| LightGBM | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 2.52 | 3.05 | -0.53 [-0.73, -0.35] | 8.2e-94 |
| LightGBM | PA-HMMQ (final) | Pooled external | HMM-src[rawE] (post hoc, same emissions) | 988 | 2.52 | 2.52 | 0.00 [-0.02, 0.02] | 6.4e-56 |
| LightGBM | PA-HMMQ (final) | Development test | CC | 160 | 2.53 | 3.09 | -0.56 [-0.89, -0.23] | 0.0071 |
| LightGBM | PA-HMMQ (final) | Development test | CC-MF | 160 | 2.53 | 2.77 | -0.24 [-0.47, -0.05] | 0.89 |
| LightGBM | PA-HMMQ (final) | Development test | PCC | 160 | 2.53 | 4.02 | -1.49 [-2.02, -0.99] | 1e-17 |
| LightGBM | PA-HMMQ (final) | Development test | PCC-iso | 160 | 2.53 | 3.76 | -1.22 [-1.82, -0.64] | 1.3e-13 |
| LightGBM | PA-HMMQ (final) | Development test | ACC | 160 | 2.53 | 3.06 | -0.53 [-0.81, -0.24] | 0.78 |
| LightGBM | PA-HMMQ (final) | Development test | PACC | 160 | 2.53 | 3.29 | -0.76 [-1.18, -0.36] | 0.0085 |
| LightGBM | PA-HMMQ (final) | Development test | EMQ | 160 | 2.53 | 2.61 | -0.08 [-0.73, 0.69] | 0.89 |
| LightGBM | PA-HMMQ (final) | Development test | HMM-src | 160 | 2.53 | 2.57 | -0.04 [-0.57, 0.51] | 0.0012 |
| LightGBM | PA-HMMQ (final) | Development test | HMM-src[rawE] (post hoc, same emissions) | 160 | 2.53 | 2.54 | -0.01 [-0.09, 0.05] | 0.39 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | CC | 93 | 4.23 | 4.51 | -0.28 [-0.54, -0.06] | 0.013 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 4.23 | 4.31 | -0.08 [-0.21, 0.04] | 0.37 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 4.23 | 5.21 | -0.97 [-1.40, -0.59] | 1.7e-09 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 4.23 | 5.13 | -0.89 [-1.43, -0.45] | 3.4e-07 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 4.23 | 4.73 | -0.50 [-0.79, -0.25] | 6.1e-05 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 4.23 | 5.04 | -0.81 [-1.25, -0.42] | 4.3e-06 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 4.23 | 4.92 | -0.69 [-1.66, 0.10] | 0.0015 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 4.23 | 4.53 | -0.29 [-0.97, 0.30] | 0.37 |
| LightGBM | PA-HMMQ (final) | SHDB-AF | HMM-src[rawE] (post hoc, same emissions) | 93 | 4.23 | 4.24 | -0.00 [-0.04, 0.05] | 0.36 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | CC | 105 | 2.88 | 3.85 | -0.97 [-1.45, -0.54] | 0.00041 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 2.88 | 3.38 | -0.49 [-0.81, -0.23] | 0.046 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 2.88 | 5.54 | -2.66 [-3.36, -2.02] | 2.3e-11 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 2.88 | 5.50 | -2.62 [-3.35, -1.91] | 2.3e-11 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 2.88 | 3.53 | -0.65 [-1.02, -0.29] | 0.052 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 2.88 | 4.26 | -1.38 [-1.94, -0.79] | 0.00041 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 2.88 | 3.78 | -0.90 [-1.69, -0.17] | 0.36 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 2.88 | 3.48 | -0.59 [-1.44, 0.47] | 8.1e-05 |
| LightGBM | PA-HMMQ (final) | CPSC2021 | HMM-src[rawE] (post hoc, same emissions) | 105 | 2.88 | 3.02 | -0.14 [-0.33, 0.02] | 0.014 |
| LightGBM | PA-HMMQ (final) | Icentia11k | CC | 790 | 2.27 | 2.69 | -0.42 [-0.51, -0.34] | 0.001 |
| LightGBM | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 2.27 | 2.46 | -0.19 [-0.24, -0.15] | 0.00013 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PCC | 790 | 2.27 | 3.58 | -1.31 [-1.45, -1.17] | 7.2e-112 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 2.27 | 3.48 | -1.21 [-1.38, -1.04] | 4.9e-112 |
| LightGBM | PA-HMMQ (final) | Icentia11k | ACC | 790 | 2.27 | 2.59 | -0.32 [-0.40, -0.25] | 5.3e-06 |
| LightGBM | PA-HMMQ (final) | Icentia11k | PACC | 790 | 2.27 | 2.86 | -0.59 [-0.72, -0.47] | 0.024 |
| LightGBM | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 2.27 | 2.72 | -0.46 [-0.68, -0.27] | 3.4e-38 |
| LightGBM | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 2.27 | 2.82 | -0.55 [-0.75, -0.38] | 2.1e-108 |
| LightGBM | PA-HMMQ (final) | Icentia11k | HMM-src[rawE] (post hoc, same emissions) | 790 | 2.27 | 2.25 | 0.02 [0.00, 0.03] | 5.2e-67 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 3.07 | 2.99 | 0.09 [-0.07, 0.26] | 0.54 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 3.07 | 2.73 | 0.34 [0.17, 0.53] | 1.1e-27 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 3.07 | 3.94 | -0.87 [-1.04, -0.69] | 6.2e-105 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 3.07 | 3.85 | -0.78 [-0.92, -0.62] | 4e-107 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 3.07 | 2.89 | 0.18 [0.03, 0.34] | 7.5e-20 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 3.07 | 3.21 | -0.14 [-0.27, -0.00] | 0.019 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 3.07 | 3.04 | 0.03 [-0.07, 0.13] | 3.4e-58 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 3.07 | 3.05 | 0.02 [0.00, 0.04] | 2.9e-43 |
| LightGBM | PA-HMMQ (pre-registered) | Pooled external | HMM-src (post hoc, same emissions) | 988 | 3.07 | 3.05 | 0.02 [0.00, 0.04] | 5.8e-44 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | CC | 160 | 2.55 | 3.09 | -0.53 [-1.17, 0.00] | 0.38 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | CC-MF | 160 | 2.55 | 2.77 | -0.22 [-0.79, 0.23] | 0.0051 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PCC | 160 | 2.55 | 4.02 | -1.47 [-2.19, -0.81] | 1.1e-14 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PCC-iso | 160 | 2.55 | 3.76 | -1.20 [-1.85, -0.59] | 4.7e-12 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | ACC | 160 | 2.55 | 3.06 | -0.51 [-1.07, -0.03] | 0.58 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | PACC | 160 | 2.55 | 3.29 | -0.74 [-1.33, -0.21] | 0.38 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | EMQ | 160 | 2.55 | 2.61 | -0.06 [-0.34, 0.24] | 0.38 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | HMM-src | 160 | 2.55 | 2.57 | -0.02 [-0.10, 0.03] | 0.38 |
| LightGBM | PA-HMMQ (pre-registered) | Development test | HMM-src (post hoc, same emissions) | 160 | 2.55 | 2.57 | -0.02 [-0.10, 0.03] | 0.079 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 4.54 | 4.51 | 0.03 [-0.50, 0.60] | 0.26 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 4.54 | 4.31 | 0.23 [-0.32, 0.86] | 0.55 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 4.54 | 5.21 | -0.66 [-1.18, -0.10] | 4.6e-07 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 4.54 | 5.13 | -0.58 [-0.99, -0.13] | 6.5e-07 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 4.54 | 4.73 | -0.19 [-0.70, 0.32] | 0.0027 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 4.54 | 5.04 | -0.50 [-0.92, -0.06] | 0.00016 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 4.54 | 4.92 | -0.38 [-0.86, 0.05] | 0.016 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 4.54 | 4.53 | 0.02 [-0.02, 0.08] | 0.51 |
| LightGBM | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src (post hoc, same emissions) | 93 | 4.54 | 4.53 | 0.02 [-0.02, 0.08] | 0.26 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 3.50 | 3.85 | -0.35 [-1.31, 0.50] | 0.46 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 3.50 | 3.38 | 0.12 [-0.90, 1.01] | 0.46 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 3.50 | 5.54 | -2.05 [-2.99, -1.22] | 3.3e-08 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 3.50 | 5.50 | -2.00 [-2.79, -1.30] | 2.1e-09 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 3.50 | 3.53 | -0.03 [-0.91, 0.73] | 0.46 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 3.50 | 4.26 | -0.76 [-1.51, -0.11] | 0.21 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 3.50 | 3.78 | -0.28 [-0.95, 0.25] | 0.023 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 3.50 | 3.48 | 0.02 [-0.07, 0.11] | 0.46 |
| LightGBM | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src (post hoc, same emissions) | 105 | 3.50 | 3.48 | 0.02 [-0.07, 0.11] | 0.15 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 2.84 | 2.69 | 0.15 [0.00, 0.32] | 0.25 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 2.84 | 2.46 | 0.38 [0.22, 0.56] | 6.5e-38 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 2.84 | 3.58 | -0.73 [-0.90, -0.55] | 8.2e-94 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 2.84 | 3.48 | -0.63 [-0.79, -0.47] | 1.3e-95 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 2.84 | 2.59 | 0.25 [0.12, 0.41] | 3.7e-34 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 2.84 | 2.86 | -0.02 [-0.14, 0.13] | 4.4e-10 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 2.84 | 2.72 | 0.12 [0.04, 0.20] | 3.6e-85 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 2.84 | 2.82 | 0.02 [0.00, 0.04] | 1.4e-51 |
| LightGBM | PA-HMMQ (pre-registered) | Icentia11k | HMM-src (post hoc, same emissions) | 790 | 2.84 | 2.82 | 0.02 [0.00, 0.04] | 2.7e-52 |
| LightGBM | PA-HMMQ[sel] | Pooled external | CC | 988 | 2.74 | 2.99 | -0.25 [-0.37, -0.13] | 0.00049 |
| LightGBM | PA-HMMQ[sel] | Pooled external | CC-MF | 988 | 2.74 | 2.73 | 0.01 [-0.10, 0.11] | 2.5e-08 |
| LightGBM | PA-HMMQ[sel] | Pooled external | PCC | 988 | 2.74 | 3.94 | -1.20 [-1.36, -1.04] | 2.5e-115 |
| LightGBM | PA-HMMQ[sel] | Pooled external | PCC-iso | 988 | 2.74 | 3.85 | -1.11 [-1.28, -0.94] | 2.3e-115 |
| LightGBM | PA-HMMQ[sel] | Pooled external | ACC | 988 | 2.74 | 2.89 | -0.15 [-0.26, -0.04] | 8e-06 |
| LightGBM | PA-HMMQ[sel] | Pooled external | PACC | 988 | 2.74 | 3.21 | -0.47 [-0.61, -0.34] | 0.87 |
| LightGBM | PA-HMMQ[sel] | Pooled external | EMQ | 988 | 2.74 | 3.04 | -0.30 [-0.52, -0.11] | 4.9e-29 |
| LightGBM | PA-HMMQ[sel] | Pooled external | HMM-src | 988 | 2.74 | 3.05 | -0.31 [-0.49, -0.15] | 1.1e-75 |
| LightGBM | PA-HMMQ[sel] | Pooled external | HMM-src[sel] (post hoc, same emissions) | 988 | 2.74 | 2.65 | 0.08 [0.05, 0.12] | 8.5e-39 |
| LightGBM | PA-HMMQ[sel] | Development test | CC | 49 | 1.96 | 2.76 | -0.81 [-1.83, -0.12] | 0.15 |
| LightGBM | PA-HMMQ[sel] | Development test | CC-MF | 49 | 1.96 | 2.23 | -0.28 [-1.05, 0.26] | 1 |
| LightGBM | PA-HMMQ[sel] | Development test | PCC | 49 | 1.96 | 3.59 | -1.64 [-2.94, -0.70] | 1.4e-05 |
| LightGBM | PA-HMMQ[sel] | Development test | PCC-iso | 49 | 1.96 | 4.26 | -2.31 [-3.60, -1.22] | 6.2e-06 |
| LightGBM | PA-HMMQ[sel] | Development test | ACC | 49 | 1.96 | 2.82 | -0.87 [-1.69, -0.27] | 0.97 |
| LightGBM | PA-HMMQ[sel] | Development test | PACC | 49 | 1.96 | 3.17 | -1.21 [-2.24, -0.46] | 0.13 |
| LightGBM | PA-HMMQ[sel] | Development test | EMQ | 49 | 1.96 | 2.23 | -0.27 [-1.07, 0.61] | 1 |
| LightGBM | PA-HMMQ[sel] | Development test | HMM-src | 49 | 1.96 | 1.80 | 0.16 [-0.50, 0.92] | 0.081 |
| LightGBM | PA-HMMQ[sel] | Development test | HMM-src[sel] (post hoc, same emissions) | 49 | 1.96 | 1.69 | 0.26 [0.03, 0.65] | 0.81 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | CC | 93 | 4.40 | 4.51 | -0.11 [-0.51, 0.36] | 0.05 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | CC-MF | 93 | 4.40 | 4.31 | 0.09 [-0.33, 0.64] | 0.22 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | PCC | 93 | 4.40 | 5.21 | -0.80 [-1.25, -0.31] | 6.6e-09 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | PCC-iso | 93 | 4.40 | 5.13 | -0.72 [-1.17, -0.29] | 5.9e-08 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | ACC | 93 | 4.40 | 4.73 | -0.33 [-0.73, 0.10] | 0.0013 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | PACC | 93 | 4.40 | 5.04 | -0.64 [-1.04, -0.23] | 4.9e-06 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | EMQ | 93 | 4.40 | 4.92 | -0.52 [-1.09, -0.00] | 0.0043 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | HMM-src | 93 | 4.40 | 4.53 | -0.12 [-0.51, 0.21] | 0.22 |
| LightGBM | PA-HMMQ[sel] | SHDB-AF | HMM-src[sel] (post hoc, same emissions) | 93 | 4.40 | 4.38 | 0.02 [-0.04, 0.11] | 0.87 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | CC | 105 | 3.69 | 3.85 | -0.16 [-0.82, 0.42] | 0.19 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | CC-MF | 105 | 3.69 | 3.38 | 0.31 [-0.29, 0.92] | 1 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | PCC | 105 | 3.69 | 5.54 | -1.86 [-2.64, -1.13] | 2e-07 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | PCC-iso | 105 | 3.69 | 5.50 | -1.81 [-2.61, -1.09] | 1.8e-07 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | ACC | 105 | 3.69 | 3.53 | 0.16 [-0.43, 0.73] | 1 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | PACC | 105 | 3.69 | 4.26 | -0.57 [-1.21, 0.05] | 0.17 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | EMQ | 105 | 3.69 | 3.78 | -0.09 [-0.92, 0.73] | 0.17 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | HMM-src | 105 | 3.69 | 3.48 | 0.21 [-0.58, 1.08] | 0.012 |
| LightGBM | PA-HMMQ[sel] | CPSC2021 | HMM-src[sel] (post hoc, same emissions) | 105 | 3.69 | 3.56 | 0.13 [-0.08, 0.34] | 0.033 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | CC | 790 | 2.42 | 2.69 | -0.28 [-0.39, -0.16] | 0.066 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | CC-MF | 790 | 2.42 | 2.46 | -0.04 [-0.13, 0.05] | 6e-15 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | PCC | 790 | 2.42 | 3.58 | -1.16 [-1.32, -1.00] | 2.2e-104 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | PCC-iso | 790 | 2.42 | 3.48 | -1.06 [-1.24, -0.89] | 5.7e-106 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | ACC | 790 | 2.42 | 2.59 | -0.17 [-0.27, -0.07] | 2.1e-14 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | PACC | 790 | 2.42 | 2.86 | -0.44 [-0.59, -0.31] | 0.00053 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | EMQ | 790 | 2.42 | 2.72 | -0.31 [-0.54, -0.11] | 4.9e-48 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | HMM-src | 790 | 2.42 | 2.82 | -0.41 [-0.61, -0.23] | 2.6e-86 |
| LightGBM | PA-HMMQ[sel] | Icentia11k | HMM-src[sel] (post hoc, same emissions) | 790 | 2.42 | 2.33 | 0.09 [0.05, 0.12] | 6.2e-49 |
| RRNet | PA-HMMQ (final) | Pooled external | CC | 988 | 3.45 | 3.96 | -0.51 [-0.59, -0.43] | 1.5e-18 |
| RRNet | PA-HMMQ (final) | Pooled external | CC-MF | 988 | 3.45 | 3.72 | -0.27 [-0.32, -0.23] | 0.014 |
| RRNet | PA-HMMQ (final) | Pooled external | PCC | 988 | 3.45 | 4.37 | -0.92 [-1.05, -0.81] | 4.5e-120 |
| RRNet | PA-HMMQ (final) | Pooled external | PCC-iso | 988 | 3.45 | 4.22 | -0.77 [-0.88, -0.67] | 1.8e-114 |
| RRNet | PA-HMMQ (final) | Pooled external | ACC | 988 | 3.45 | 3.85 | -0.40 [-0.48, -0.33] | 0.82 |
| RRNet | PA-HMMQ (final) | Pooled external | PACC | 988 | 3.45 | 4.10 | -0.65 [-0.76, -0.55] | 0.014 |
| RRNet | PA-HMMQ (final) | Pooled external | EMQ | 988 | 3.45 | 3.63 | -0.18 [-0.31, -0.08] | 3.9e-29 |
| RRNet | PA-HMMQ (final) | Pooled external | HMM-src | 988 | 3.45 | 3.73 | -0.28 [-0.38, -0.19] | 4.1e-78 |
| RRNet | PA-HMMQ (final) | Pooled external | HMM-src[rawE] (post hoc, same emissions) | 988 | 3.45 | 3.43 | 0.02 [-0.00, 0.04] | 9.2e-33 |
| RRNet | PA-HMMQ (final) | Development test | CC | 160 | 2.71 | 3.19 | -0.48 [-0.89, -0.16] | 0.33 |
| RRNet | PA-HMMQ (final) | Development test | CC-MF | 160 | 2.71 | 2.93 | -0.21 [-0.45, -0.04] | 0.87 |
| RRNet | PA-HMMQ (final) | Development test | PCC | 160 | 2.71 | 3.69 | -0.97 [-1.43, -0.58] | 2.1e-12 |
| RRNet | PA-HMMQ (final) | Development test | PCC-iso | 160 | 2.71 | 3.23 | -0.51 [-0.97, 0.03] | 2.1e-10 |
| RRNet | PA-HMMQ (final) | Development test | ACC | 160 | 2.71 | 3.18 | -0.47 [-0.87, -0.16] | 0.54 |
| RRNet | PA-HMMQ (final) | Development test | PACC | 160 | 2.71 | 3.36 | -0.65 [-1.07, -0.28] | 0.08 |
| RRNet | PA-HMMQ (final) | Development test | EMQ | 160 | 2.71 | 2.57 | 0.14 [-0.68, 1.18] | 0.87 |
| RRNet | PA-HMMQ (final) | Development test | HMM-src | 160 | 2.71 | 2.07 | 0.64 [-0.12, 1.70] | 8.2e-05 |
| RRNet | PA-HMMQ (final) | Development test | HMM-src[rawE] (post hoc, same emissions) | 160 | 2.71 | 2.45 | 0.26 [-0.01, 0.69] | 0.34 |
| RRNet | PA-HMMQ (final) | SHDB-AF | CC | 93 | 4.31 | 4.78 | -0.47 [-0.76, -0.22] | 0.00057 |
| RRNet | PA-HMMQ (final) | SHDB-AF | CC-MF | 93 | 4.31 | 4.52 | -0.20 [-0.36, -0.07] | 0.0076 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PCC | 93 | 4.31 | 5.06 | -0.75 [-1.14, -0.41] | 1.6e-08 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PCC-iso | 93 | 4.31 | 5.00 | -0.69 [-1.07, -0.36] | 2.4e-08 |
| RRNet | PA-HMMQ (final) | SHDB-AF | ACC | 93 | 4.31 | 4.97 | -0.66 [-0.95, -0.41] | 6.4e-07 |
| RRNet | PA-HMMQ (final) | SHDB-AF | PACC | 93 | 4.31 | 5.18 | -0.87 [-1.25, -0.54] | 3.4e-07 |
| RRNet | PA-HMMQ (final) | SHDB-AF | EMQ | 93 | 4.31 | 4.85 | -0.53 [-1.14, -0.00] | 0.0046 |
| RRNet | PA-HMMQ (final) | SHDB-AF | HMM-src | 93 | 4.31 | 4.55 | -0.24 [-0.62, 0.09] | 0.14 |
| RRNet | PA-HMMQ (final) | SHDB-AF | HMM-src[rawE] (post hoc, same emissions) | 93 | 4.31 | 4.29 | 0.03 [-0.02, 0.07] | 0.88 |
| RRNet | PA-HMMQ (final) | CPSC2021 | CC | 105 | 4.20 | 5.01 | -0.81 [-1.22, -0.46] | 0.00048 |
| RRNet | PA-HMMQ (final) | CPSC2021 | CC-MF | 105 | 4.20 | 4.73 | -0.53 [-0.78, -0.32] | 0.0018 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PCC | 105 | 4.20 | 5.86 | -1.66 [-2.22, -1.16] | 4.6e-10 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PCC-iso | 105 | 4.20 | 5.50 | -1.30 [-1.82, -0.83] | 7.1e-09 |
| RRNet | PA-HMMQ (final) | CPSC2021 | ACC | 105 | 4.20 | 4.81 | -0.61 [-0.99, -0.28] | 0.038 |
| RRNet | PA-HMMQ (final) | CPSC2021 | PACC | 105 | 4.20 | 5.27 | -1.07 [-1.58, -0.63] | 0.002 |
| RRNet | PA-HMMQ (final) | CPSC2021 | EMQ | 105 | 4.20 | 4.51 | -0.31 [-0.83, 0.14] | 0.002 |
| RRNet | PA-HMMQ (final) | CPSC2021 | HMM-src | 105 | 4.20 | 4.49 | -0.29 [-0.69, 0.09] | 0.0018 |
| RRNet | PA-HMMQ (final) | CPSC2021 | HMM-src[rawE] (post hoc, same emissions) | 105 | 4.20 | 4.21 | -0.01 [-0.17, 0.17] | 0.0088 |
| RRNet | PA-HMMQ (final) | Icentia11k | CC | 790 | 3.25 | 3.72 | -0.47 [-0.56, -0.39] | 2.4e-11 |
| RRNet | PA-HMMQ (final) | Icentia11k | CC-MF | 790 | 3.25 | 3.50 | -0.25 [-0.30, -0.20] | 0.98 |
| RRNet | PA-HMMQ (final) | Icentia11k | PCC | 790 | 3.25 | 4.10 | -0.85 [-0.98, -0.73] | 2.5e-106 |
| RRNet | PA-HMMQ (final) | Icentia11k | PCC-iso | 790 | 3.25 | 3.96 | -0.71 [-0.82, -0.61] | 6.3e-102 |
| RRNet | PA-HMMQ (final) | Icentia11k | ACC | 790 | 3.25 | 3.59 | -0.34 [-0.42, -0.27] | 0.0002 |
| RRNet | PA-HMMQ (final) | Icentia11k | PACC | 790 | 3.25 | 3.82 | -0.57 [-0.68, -0.46] | 0.57 |
| RRNet | PA-HMMQ (final) | Icentia11k | EMQ | 790 | 3.25 | 3.37 | -0.13 [-0.24, -0.03] | 6.2e-41 |
| RRNet | PA-HMMQ (final) | Icentia11k | HMM-src | 790 | 3.25 | 3.53 | -0.29 [-0.38, -0.20] | 7.1e-90 |
| RRNet | PA-HMMQ (final) | Icentia11k | HMM-src[rawE] (post hoc, same emissions) | 790 | 3.25 | 3.22 | 0.02 [0.01, 0.04] | 9.5e-39 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | CC | 988 | 3.78 | 3.96 | -0.18 [-0.28, -0.09] | 5.3e-08 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | CC-MF | 988 | 3.78 | 3.72 | 0.05 [-0.03, 0.14] | 8e-06 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PCC | 988 | 3.78 | 4.37 | -0.60 [-0.73, -0.48] | 1.7e-103 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PCC-iso | 988 | 3.78 | 4.22 | -0.45 [-0.57, -0.33] | 9.2e-91 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | ACC | 988 | 3.78 | 3.85 | -0.08 [-0.16, 0.01] | 1.2e-09 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | PACC | 988 | 3.78 | 4.10 | -0.32 [-0.43, -0.22] | 0.37 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | EMQ | 988 | 3.78 | 3.63 | 0.14 [0.06, 0.22] | 1.3e-64 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | HMM-src | 988 | 3.78 | 3.73 | 0.04 [0.02, 0.07] | 3.4e-21 |
| RRNet | PA-HMMQ (pre-registered) | Pooled external | HMM-src (post hoc, same emissions) | 988 | 3.78 | 3.73 | 0.04 [0.02, 0.07] | 6.8e-22 |
| RRNet | PA-HMMQ (pre-registered) | Development test | CC | 160 | 2.15 | 3.19 | -1.05 [-2.22, -0.18] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | CC-MF | 160 | 2.15 | 2.93 | -0.78 [-1.91, 0.06] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PCC | 160 | 2.15 | 3.69 | -1.54 [-2.65, -0.72] | 2e-10 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PCC-iso | 160 | 2.15 | 3.23 | -1.08 [-1.75, -0.51] | 4.9e-11 |
| RRNet | PA-HMMQ (pre-registered) | Development test | ACC | 160 | 2.15 | 3.18 | -1.04 [-2.16, -0.18] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | PACC | 160 | 2.15 | 3.36 | -1.21 [-2.27, -0.45] | 0.94 |
| RRNet | PA-HMMQ (pre-registered) | Development test | EMQ | 160 | 2.15 | 2.57 | -0.43 [-1.04, 0.00] | 0.23 |
| RRNet | PA-HMMQ (pre-registered) | Development test | HMM-src | 160 | 2.15 | 2.07 | 0.07 [-0.02, 0.19] | 1 |
| RRNet | PA-HMMQ (pre-registered) | Development test | HMM-src (post hoc, same emissions) | 160 | 2.15 | 2.07 | 0.07 [-0.02, 0.19] | 0.25 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | CC | 93 | 4.60 | 4.78 | -0.18 [-0.54, 0.26] | 0.00097 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | CC-MF | 93 | 4.60 | 4.52 | 0.08 [-0.22, 0.47] | 0.43 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PCC | 93 | 4.60 | 5.06 | -0.46 [-0.89, 0.03] | 4.2e-08 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PCC-iso | 93 | 4.60 | 5.00 | -0.41 [-0.86, 0.15] | 2.9e-06 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | ACC | 93 | 4.60 | 4.97 | -0.37 [-0.69, 0.04] | 3.6e-05 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | PACC | 93 | 4.60 | 5.18 | -0.59 [-0.95, -0.15] | 2.9e-06 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | EMQ | 93 | 4.60 | 4.85 | -0.25 [-0.59, 0.07] | 0.0096 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src | 93 | 4.60 | 4.55 | 0.04 [-0.00, 0.10] | 0.52 |
| RRNet | PA-HMMQ (pre-registered) | SHDB-AF | HMM-src (post hoc, same emissions) | 93 | 4.60 | 4.55 | 0.04 [-0.00, 0.10] | 0.52 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | CC | 105 | 4.59 | 5.01 | -0.42 [-0.90, 0.04] | 0.096 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | CC-MF | 105 | 4.59 | 4.73 | -0.15 [-0.56, 0.24] | 0.82 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PCC | 105 | 4.59 | 5.86 | -1.27 [-1.88, -0.67] | 6.8e-09 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PCC-iso | 105 | 4.59 | 5.50 | -0.91 [-1.51, -0.32] | 2.3e-07 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | ACC | 105 | 4.59 | 4.81 | -0.22 [-0.66, 0.20] | 0.82 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | PACC | 105 | 4.59 | 5.27 | -0.68 [-1.20, -0.19] | 0.18 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | EMQ | 105 | 4.59 | 4.51 | 0.08 [-0.32, 0.45] | 5.7e-06 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src | 105 | 4.59 | 4.49 | 0.10 [-0.03, 0.26] | 0.51 |
| RRNet | PA-HMMQ (pre-registered) | CPSC2021 | HMM-src (post hoc, same emissions) | 105 | 4.59 | 4.49 | 0.10 [-0.03, 0.26] | 0.17 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | CC | 790 | 3.57 | 3.72 | -0.15 [-0.24, -0.05] | 0.00019 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | CC-MF | 790 | 3.57 | 3.50 | 0.07 [-0.00, 0.16] | 6.6e-11 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PCC | 790 | 3.57 | 4.10 | -0.52 [-0.65, -0.40] | 8.9e-90 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PCC-iso | 790 | 3.57 | 3.96 | -0.39 [-0.51, -0.27] | 5.6e-81 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | ACC | 790 | 3.57 | 3.59 | -0.02 [-0.10, 0.06] | 1.8e-20 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | PACC | 790 | 3.57 | 3.82 | -0.25 [-0.34, -0.15] | 7e-06 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | EMQ | 790 | 3.57 | 3.37 | 0.20 [0.13, 0.26] | 3.2e-84 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | HMM-src | 790 | 3.57 | 3.53 | 0.04 [0.02, 0.06] | 8.1e-27 |
| RRNet | PA-HMMQ (pre-registered) | Icentia11k | HMM-src (post hoc, same emissions) | 790 | 3.57 | 3.53 | 0.04 [0.02, 0.06] | 1.6e-27 |
| RRNet | PA-HMMQ[sel] | Pooled external | CC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | CC-MF | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | PCC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | PCC-iso | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | ACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | PACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | EMQ | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | HMM-src | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Pooled external | HMM-src[sel] (post hoc, same emissions) | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | CC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | CC-MF | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | PCC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | PCC-iso | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | ACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | PACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | EMQ | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | HMM-src | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Development test | HMM-src[sel] (post hoc, same emissions) | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | CC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | CC-MF | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | PCC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | PCC-iso | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | ACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | PACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | EMQ | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | HMM-src | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | SHDB-AF | HMM-src[sel] (post hoc, same emissions) | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | CC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | CC-MF | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | PCC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | PCC-iso | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | ACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | PACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | EMQ | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | HMM-src | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | CPSC2021 | HMM-src[sel] (post hoc, same emissions) | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | CC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | CC-MF | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | PCC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | PCC-iso | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | ACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | PACC | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | EMQ | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | HMM-src | 0 | – | – | nan [nan, nan] | 1 |
| RRNet | PA-HMMQ[sel] | Icentia11k | HMM-src[sel] (post hoc, same emissions) | 0 | – | – | nan [nan, nan] | 1 |

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


