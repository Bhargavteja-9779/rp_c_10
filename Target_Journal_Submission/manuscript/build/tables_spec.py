"""Which machine-generated tables appear in the manuscript / supplement, with titles and notes."""
EST_NAMES = {"PA-HMMQ[rawE]": "PA-HMMQ (final)", "PA-HMMQ": "PA-HMMQ (pre-registered)"}


def _rename_est(df, col):
    df[col] = df[col].replace({"PA-HMMQ[rawE] (final)": "PA-HMMQ (final)", "PA-HMMQ (pre-registered)": "PA-HMMQ (pre-registered)",
                               "PA-HMMQ[rawE]": "PA-HMMQ (final)", "PA-HMMQ": "PA-HMMQ (pre-registered)"})
    return df


COH = {"dev_test": "Development test", "ext_shdb-af": "SHDB-AF", "ext_cpsc2021": "CPSC2021", "ext_icentia11k": "Icentia11k",
       "ext_pooled": "Pooled external", "calB": "Calibration B"}


def tables(tb):
    T = []
    T.append(tb("tableS1_databases", "Table 1 Databases, cohorts and reference rhythm characteristics",
                "Counts after exclusions (invalid RR intervals, unlabelled rhythm segments, one duplicate SHDB-AF recording). Windows are 60 consecutive valid RR intervals. AF, atrial fibrillation; AFL, atrial flutter.",
                keep_cols=["Database", "Role", "Country", "Recordings", "Patients", "Hours analysed", "Patients with AF", "Patients with AFL", "AF windows (%)"]))
    T.append(tb("table3_burden_mae_LightGBM", "Table 2 Per-patient AF-burden mean absolute error (percentage points) by estimator and cohort, LightGBM detector",
                "Mean ± SD over five pre-specified seeds of the per-seed mean absolute error. Development test: held-out development patients (USA). CC, classify-and-count; CC-MF, CC after 3-window median filter; PCC, probabilistic CC; PCC-iso, PCC after isotonic recalibration on source calibration patients; ACC/PACC, adjusted (probabilistic) CC; EMQ, expectation–maximisation prior adjustment; HMM-src, hidden Markov model with fixed source dynamics; PA-HMMQ, patient-adaptive HMM quantifier.",
                rename=COH, filt=lambda d: _rename_est(d.assign(Estimator=d.Estimator), "Estimator")))
    T.append(tb("table4_agreement_pooled_external", "Table 3 Agreement with the reference AF burden in the pooled external cohorts (LightGBM detector)",
                "Mean ± SD over seeds. pp, percentage points; LoA, Bland–Altman limits of agreement; CCC, Lin's concordance correlation coefficient. False burden: mean estimated burden in patients without any reference AF.",
                filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table5_primary_tests", "Table 4 Primary pre-specified comparison: final PA-HMMQ vs each comparator, pooled external cohorts (LightGBM)",
                "Unit of analysis: patient (absolute errors averaged over the five seeds). Two-sided Wilcoxon signed-rank tests, Holm-adjusted across the eight comparators. Paired difference = PA-HMMQ − comparator (negative favours PA-HMMQ); 95% CI by patient-level bootstrap (2000 resamples). Rank-biserial r < 0 indicates that PA-HMMQ has the smaller error in the majority of rank-weighted pairs.",
                keep_cols=["Comparator", "n patients", "Mean AE proposed (pp)", "Mean AE comparator (pp)", "Mean paired diff (pp) [95% CI]", "Median paired diff (pp) [95% CI]", "Rank-biserial r", "p (Holm)"],
                filt=lambda d: d[d.Proposed == "PA-HMMQ[rawE]"]))
    keep = ["CC+conformal(const)", "PA-HMMQ posterior 90% CrI", "PA-HMMQ+conformal(norm)", "PA-HMMQ[rawE]+conformal(const)", "PA-HMMQ[rawE]+conformal(norm)"]
    ren = {"CC+conformal(const)": "CC + constant-width conformal", "PA-HMMQ posterior 90% CrI": "PA-HMMQ (pre-reg.) posterior 90% credible interval",
           "PA-HMMQ+conformal(norm)": "PA-HMMQ (pre-reg.) + normalised conformal", "PA-HMMQ[rawE]+conformal(const)": "PA-HMMQ (final) + constant-width conformal",
           "PA-HMMQ[rawE]+conformal(norm)": "PA-HMMQ (final) + normalised conformal (proposed)"}
    T.append(tb("table7_intervals", "Table 5 Coverage and width of 90% per-patient burden intervals (LightGBM detector)",
                "Target coverage 0.90. Conformal quantiles were computed on calibration-B patients only. Coverage: mean ± SD over seeds; Clopper–Pearson 95% CI computed from the seed-averaged coverage and the number of patients. Width in percentage points.",
                keep_cols=["Method", "Cohort", "n", "Coverage (mean ± SD over seeds)", "Clopper–Pearson 95% CI", "Coverage AF-free", "Coverage AF", "Mean width (pp)", "Median width (pp)"],
                filt=lambda d: d[d.Method.isin(keep) & d.Cohort.isin(["dev_test", "ext_shdb-af", "ext_cpsc2021", "ext_icentia11k", "ext_pooled"])].assign(Method=lambda x: x.Method.map(ren), Cohort=lambda x: x.Cohort.map(COH))))
    return T


def supp_tables(tb):
    T = []
    T.append(tb("tableS1_databases", "Table S1 Databases: sources, versions, licences and window counts",
                "All databases from PhysioNet; counts after exclusions (see Supplementary S2). ODC-By, Open Data Commons Attribution License; CC BY, Creative Commons Attribution; CC BY-NC-SA, Creative Commons Attribution-NonCommercial-ShareAlike."))
    T.append(tb("table2_window_metrics", "Table S2 Window-level detector performance (mean ± SD over seeds)",
                "Threshold 0.5. ECE, expected calibration error (15 bins).", filt=lambda d: d.assign(Cohort=d.Cohort.map(COH))))
    for i, det in enumerate(["Classical-LR", "RRNet"]):
        T.append(tb(f"table3_burden_mae_{det}", f"Table S{3+i} Per-patient AF-burden MAE (pp) by estimator, {det} detector",
                    "Mean ± SD over seeds.", rename=COH, filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table8_ablation", "Table S5 Ablation of PA-HMMQ components (LightGBM, MAE in pp)",
                "k, prior strength κ in pseudo-transitions (κ=10 pre-specified); rawE, detector probability used as emission likelihood (final variant); HMM-src, no per-patient adaptation (κ→∞); EMQ, per-patient prior adaptation without temporal model; CC, no quantification.",
                rename=COH))
    T.append(tb("table9_burden_strata", "Table S6 MAE (pp) by reference burden stratum, pooled external cohorts (LightGBM)", "Mean over seeds.", filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table6_threshold_classification", "Table S7 Classification of patients by burden thresholds, pooled external cohorts (LightGBM)",
                "present_30s: ≥30 s of AF in the analysed recording; ge1pct/ge10pct: burden ≥1%/≥10%. Mean ± SD over seeds.", filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table14_afl_sensitivity", "Table S8 Influence of atrial flutter (LightGBM, pooled external)",
                "The AF+AFL reference counts flutter time as arrhythmia time. The analysis excluding patients with any flutter is post hoc.", filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table12_robustness", "Table S9 Robustness to simulated R-peak and rhythm perturbations, SHDB-AF (MAE in pp, mean ± SD over seeds)",
                "missed/false: probability of deleting/inserting an R peak per beat; jitter: SD of Gaussian R-peak timing noise (s); ectopy: probability of a premature beat with compensatory pause.",
                rename=EST_NAMES))
    T.append(tb("table13_robustness_intervals", "Table S10 Coverage of normalised conformal intervals under perturbation, SHDB-AF", "Target 0.90."))
    T.append(tb("table11_sensitivity_trainfrac_window", "Table S11 Sensitivity to training-set size and window length (LightGBM, MAE in pp)",
                "Reduced-data and window-length runs used SHDB-AF and CPSC2021 as external cohorts (Icentia11k omitted for computational reasons).", rename=COH, filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("tableS_shdb_subgroups", "Table S12 Subgroup MAE (pp) in SHDB-AF by sex and age (LightGBM)", "Age split at the cohort median.", filt=lambda d: _rename_est(d, "Estimator")))
    T.append(tb("table10_worst_patients", "Table S13 The 15 external patients with the largest absolute error of the final PA-HMMQ (LightGBM, seed-averaged)",
                "ae, absolute error (pp); err, signed error (pp); true_burden, fraction; ectopy and AFL as fractions of beats/time."))
    T.append(tb("tableS_all_tests", "Table S14 All paired comparisons (all detectors, cohorts and both PA-HMMQ variants)", "As Table 4.",
                keep_cols=["Detector", "Proposed", "Cohort", "Comparator", "n patients", "Mean AE proposed (pp)", "Mean AE comparator (pp)", "Mean paired diff (pp) [95% CI]", "p (Holm)"],
                filt=lambda d: _rename_est(_rename_est(d, "Proposed").assign(Cohort=lambda x: x.Cohort.map(COH)), "Proposed")))
    T.append(tb("table15_R1_emission_selection", "Table S15 Revision R1 (post hoc): emission model selected on calibration-A patients per seed and detector",
                "Mean per-patient burden error of the fixed-dynamics HMM on calibration-A patients for each candidate emission (hist: calibration-set histogram; T: likelihood ratio (p/(1−p))^(1/T))."))
    T.append(tb("table16_newly_missed", "Table S16 External patients with ≥30 s of reference AF classified as AF-present by classify-and-count but AF-free by the final PA-HMMQ (LightGBM, seed-majority; post hoc)",
                "true_burden as a fraction of analysed time; af_minutes, reference AF time; hours, analysed time."))
    T.append(tb("table17_rounded_tests", "Table S17 Post-hoc paired comparisons with burden estimates reported at 0.1-percentage-point resolution (LightGBM, pooled external cohorts)",
                "Same procedure as Table 4 after rounding each estimate to 0.001 (0.1 pp); fair comparator (same emissions, fixed dynamics) not included in the Holm family.", filt=lambda d: _rename_est(d, "Proposed")))
    T.append(tb("table18_local_recalibration", "Table S18 Post-hoc local recalibration of the normalised conformal quantile in each external cohort (final PA-HMMQ, LightGBM)",
                "For each seed, n locally labelled patients were drawn at random (200 repeats) to compute the conformal quantile; coverage and width evaluated on the remaining patients of the cohort. Target coverage 0.90.",
                filt=lambda d: d.assign(Cohort=d.Cohort.map(COH))))
    T.append(tb("table19_median_filter_lengths", "Table S19 Post-hoc comparison of median-filter lengths for classify-and-count (LightGBM, mean over seeds)",
                "Filter length selected on development patients (calibration B and development test) before inspecting the external results of this analysis."))
    return T
