"""Generate all tables, statistics and summary metrics from machine-readable results.

Nothing in the manuscript is typed by hand: every number is produced here (tables/*.csv|md,
results/metrics.json, results/statistics.json) or in src/visualization/figures.py.
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.statistics.tests import paired_wilcoxon, holm, mcnemar, clopper_pearson, bootstrap_mean_ci
from src.evaluation.metrics import burden_metrics
from scipy import stats

BASELINES = ["CC", "CC-MF", "PCC", "PCC-iso", "ACC", "PACC", "EMQ", "HMM-src"]
PA_PRE, PA_RAW, PA_SEL = "PA-HMMQ", "PA-HMMQ[rawE]", "PA-HMMQ[sel]"
FAIR = {"PA-HMMQ": "HMM-src", "PA-HMMQ[rawE]": "HMM-src[rawE]", "PA-HMMQ[sel]": "HMM-src[sel]"}  # same emissions, fixed dynamics
EXT = ["ext_shdb-af", "ext_cpsc2021", "ext_icentia11k"]
COH = ["dev_test"] + EXT


def fmt(m, s, d=2):
    return f"{m:.{d}f} ± {s:.{d}f}"


def md_table(df, path, floatfmt=None):
    df.to_csv(path + ".csv", index=False)
    with open(path + ".md", "w") as f:
        cols = list(df.columns)
        f.write("| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n")
        for _, r in df.iterrows():
            f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")


def load(res):
    R = pd.read_csv(os.path.join(res, "raw_results.csv"))
    rp = os.path.join(res, "revision_results.csv")
    if os.path.exists(rp):  # Revision R1 (post hoc)
        R = pd.concat([R, pd.read_csv(rp)], ignore_index=True)
    R["err"] = (R.estimate - R.true_burden) * 100
    R["ae"] = R.err.abs()
    R["ae_afafl"] = (R.estimate - R.true_burden_af_afl).abs() * 100
    return R


def pooled(R):
    e = R[R.cohort.isin(EXT)].copy(); e["cohort"] = "ext_pooled"
    return pd.concat([R, e])


def main(res, tab, cfg_primary="LightGBM"):
    os.makedirs(tab, exist_ok=True)
    R = load(res)
    S, M = {}, {}
    # ---------------- Amendment A1 decision (development data only) ----------------
    dev = R[(R.detector == cfg_primary) & R.cohort.isin(["calB", "dev_test"]) & R.estimator.isin([PA_PRE, PA_RAW])]
    dm = dev.groupby("estimator").ae.mean()
    FINAL = PA_RAW if dm[PA_RAW] < dm[PA_PRE] else PA_PRE
    S["amendment_A1"] = dict(rule="lower mean per-patient AE on calB ∪ dev_test, LightGBM, pooled over seeds",
                             dev_mae_pre_registered=float(dm[PA_PRE]), dev_mae_raw_emission=float(dm[PA_RAW]), chosen=FINAL)
    print("A1 decision:", S["amendment_A1"])
    RP = pooled(R)
    has_sel = PA_SEL in set(R.estimator)
    EST_MAIN = BASELINES + ["HMM-src[rawE]"] + (["HMM-src[sel]"] if has_sel else []) + [PA_PRE, PA_RAW] + ([PA_SEL] if has_sel else [])

    # ---------------- Table: cohort characteristics ----------------
    one = RP[(RP.seed == RP.seed.min()) & (RP.detector == cfg_primary) & (RP.estimator == "CC")]
    rows = []
    for c in ["calB", "dev_test"] + EXT + ["ext_pooled"]:
        x = one[one.cohort == c]
        rows.append({"Cohort": c, "Patients": len(x), "Hours analysed (median [IQR])": f"{x.hours.median():.1f} [{x.hours.quantile(.25):.1f}–{x.hours.quantile(.75):.1f}]",
                     "Total hours": f"{x.hours.sum():.0f}", "Patients with any AF": int((x.true_burden > 0).sum()),
                     "AF burden, median [IQR] (%)": f"{100*x.true_burden.median():.1f} [{100*x.true_burden.quantile(.25):.1f}–{100*x.true_burden.quantile(.75):.1f}]",
                     "AF burden among AF patients, median (%)": f"{100*x.true_burden[x.true_burden>0].median():.1f}" if (x.true_burden > 0).any() else "–",
                     "Patients with AFL": int((x.afl_burden > 0).sum()),
                     "SV ectopy, median (%)": f"{100*x.ectopy_sv.median():.2f}", "V ectopy, median (%)": f"{100*x.ectopy_v.median():.2f}"})
    md_table(pd.DataFrame(rows), os.path.join(tab, "table1_cohorts"))
    # full development pool (all dev patients, from caches) is written by dataset_summary()

    # ---------------- Window-level detector performance ----------------
    W = pd.read_csv(os.path.join(res, "window_metrics.csv"))
    rows = []
    for (det, c), g in W.groupby(["detector", "cohort"]):
        rows.append({"Detector": det, "Cohort": c, **{k: fmt(g[k].mean(), g[k].std(), 3) for k in ["auroc", "auprc", "sensitivity", "specificity", "f1", "ece", "brier"]}})
    wt = pd.DataFrame(rows); wt["o"] = wt.Cohort.map({c: i for i, c in enumerate(COH)}); wt = wt.sort_values(["Detector", "o"]).drop(columns="o")
    md_table(wt, os.path.join(tab, "table2_window_metrics"))
    M["window_metrics"] = {f"{det}|{c}": {k: [float(g[k].mean()), float(g[k].std())] for k in ["auroc", "auprc", "sensitivity", "specificity", "f1", "ece", "brier"]}
                           for (det, c), g in W.groupby(["detector", "cohort"])}

    # ---------------- Main burden table (per-seed MAE, mean ± SD over seeds) ----------------
    per_seed = RP.groupby(["detector", "estimator", "cohort", "seed"]).apply(
        lambda g: pd.Series(burden_metrics(g.true_burden.values, g.estimate.values, g.hours.values)), include_groups=False).reset_index()
    per_seed.to_csv(os.path.join(res, "burden_metrics_per_seed.csv"), index=False)
    M["burden"] = {}
    for (det, est, c), g in per_seed.groupby(["detector", "estimator", "cohort"]):
        M["burden"][f"{det}|{est}|{c}"] = {k: [float(g[k].mean()), float(g[k].std())] for k in g.columns if k not in ("detector", "estimator", "cohort", "seed") and np.issubdtype(g[k].dtype, np.number)}
    for det in sorted(R.detector.unique()):
        rows = []
        for est in EST_MAIN:
            r = {"Estimator": est + (" (final)" if est == FINAL else "") + (" (pre-registered)" if est == PA_PRE else "") + (" (post hoc R1)" if est in (PA_SEL, "HMM-src[sel]") else "")}
            for c in COH + ["ext_pooled"]:
                g = per_seed[(per_seed.detector == det) & (per_seed.estimator == est) & (per_seed.cohort == c)]
                r[c] = fmt(g.mae_pp.mean(), g.mae_pp.std())
            rows.append(r)
        md_table(pd.DataFrame(rows), os.path.join(tab, f"table3_burden_mae_{det}"))
    # agreement details (pooled external, primary detector)
    rows = []
    for est in EST_MAIN:
        g = per_seed[(per_seed.detector == cfg_primary) & (per_seed.estimator == est) & (per_seed.cohort == "ext_pooled")]
        rows.append({"Estimator": est, "MAE (pp)": fmt(g.mae_pp.mean(), g.mae_pp.std()), "Median AE (pp)": fmt(g.median_ae_pp.mean(), g.median_ae_pp.std()),
                     "RMSE (pp)": fmt(g.rmse_pp.mean(), g.rmse_pp.std()), "Bias (pp)": fmt(g.bias_pp.mean(), g.bias_pp.std()),
                     "95% LoA (pp)": f"{g.loa_low_pp.mean():.2f} to {g.loa_high_pp.mean():.2f}", "Lin's CCC": fmt(g.ccc.mean(), g.ccc.std(), 3),
                     "False burden in AF-free patients (pp)": fmt(g.af_free_mean_false_burden_pp.mean(), g.af_free_mean_false_burden_pp.std(), 3),
                     "MAE in AF patients (pp)": fmt(g.mae_af_present_pp.mean(), g.mae_af_present_pp.std())})
    md_table(pd.DataFrame(rows), os.path.join(tab, "table4_agreement_pooled_external"))

    # ---------------- Primary statistical tests ----------------
    def seed_avg(det, est, cohorts, col="ae"):
        x = RP[(RP.detector == det) & (RP.estimator == est) & RP.cohort.isin(cohorts)]
        return x.groupby("patient")[col].mean().sort_index()
    S["tests"] = {}
    rows = []
    for det in sorted(R.detector.unique()):
        for target in ([FINAL, PA_PRE] if FINAL != PA_PRE else [PA_PRE]) + ([PA_SEL] if has_sel else []):
            for cname, cset in [("ext_pooled", EXT)] + [(c, [c]) for c in COH]:
                a = seed_avg(det, target, cset)
                res_ = {}
                for b in BASELINES:
                    bb = seed_avg(det, b, cset).loc[a.index]
                    res_[b] = paired_wilcoxon(a.values, bb.values, n_boot=2000, seed=0)
                adj = holm({b: v["p"] for b, v in res_.items()})
                for b, v in res_.items():
                    v["p_holm"] = adj[b]
                # post hoc: fair comparator with identical emissions and fixed dynamics (isolates patient adaptation)
                fb = FAIR[target]
                fv = paired_wilcoxon(a.values, seed_avg(det, fb, cset).loc[a.index].values, n_boot=2000, seed=0)
                fv["p_holm"] = fv["p"]; res_[fb + " (post hoc, same emissions)"] = fv
                for b, v in res_.items():
                    bname = b.split(" (post hoc")[0]
                    rows.append({"Detector": det, "Proposed": target, "Cohort": cname, "Comparator": b, "n patients": v["n"],
                                 "Mean AE proposed (pp)": f"{a.mean():.2f}", "Mean AE comparator (pp)": f"{seed_avg(det, bname, cset).loc[a.index].mean():.2f}",
                                 "Median paired diff (pp) [95% CI]": f"{v['median_diff']:.3f} [{v['median_ci'][0]:.3f}, {v['median_ci'][1]:.3f}]",
                                 "Mean paired diff (pp) [95% CI]": f"{v['mean_diff']:.2f} [{v['mean_ci'][0]:.2f}, {v['mean_ci'][1]:.2f}]",
                                 "Rank-biserial r": f"{v['rank_biserial']:.3f}", "p (Wilcoxon)": f"{v['p']:.2g}", "p (Holm)": f"{v['p_holm']:.2g}",
                                 "Non-zero pairs": v["n_nonzero"]})
                S["tests"][f"{det}|{target}|{cname}"] = res_
    T = pd.DataFrame(rows)
    md_table(T[(T.Detector == cfg_primary) & (T.Cohort == "ext_pooled")], os.path.join(tab, "table5_primary_tests"))
    md_table(T, os.path.join(tab, "tableS_all_tests"))

    # ---------------- Threshold classification ----------------
    rows = []; S["mcnemar"] = {}
    thr_list = [("present_30s", None), ("ge1pct", 0.01), ("ge10pct", 0.10)]
    for est in ["CC", "CC-MF", "PCC-iso", "ACC", "EMQ", "HMM-src", "HMM-src[rawE]", PA_PRE, PA_RAW] + ([PA_SEL] if has_sel else []):
        g = per_seed[(per_seed.detector == cfg_primary) & (per_seed.estimator == est) & (per_seed.cohort == "ext_pooled")]
        r = {"Estimator": est}
        for t, _ in thr_list:
            r[f"{t} sens"] = fmt(g[f"{t}_sens"].mean(), g[f"{t}_sens"].std(), 3); r[f"{t} spec"] = fmt(g[f"{t}_spec"].mean(), g[f"{t}_spec"].std(), 3)
        rows.append(r)
    md_table(pd.DataFrame(rows), os.path.join(tab, "table6_threshold_classification"))
    x = RP[(RP.detector == cfg_primary) & (RP.cohort == "ext_pooled")]
    for t, thr in thr_list:
        def votes(est):
            g = x[x.estimator == est].copy()
            if thr is None:
                g["pred"] = g.estimate * g.hours * 3600 >= 30; g["truth"] = g.true_burden * g.hours * 3600 >= 30
            else:
                g["pred"] = g.estimate >= thr; g["truth"] = g.true_burden >= thr
            v = g.groupby("patient").agg(pred=("pred", "mean"), truth=("truth", "first")).sort_index()
            return (v.pred >= 0.5).values, v.truth.values
        pa, tr = votes(FINAL); pc, _ = votes("CC")
        S["mcnemar"][f"{FINAL}_vs_CC|{t}"] = mcnemar(pa, pc, tr)

    # ---------------- Intervals ----------------
    I = pd.read_csv(os.path.join(res, "intervals.csv"))
    if os.path.exists(os.path.join(res, "revision_intervals.csv")):
        I = pd.concat([I, pd.read_csv(os.path.join(res, "revision_intervals.csv"))], ignore_index=True)
    I["cov"] = (I.true_burden >= I.lo - 1e-12) & (I.true_burden <= I.hi + 1e-12); I["width"] = (I.hi - I.lo) * 100
    Ie = I[I.cohort.isin(EXT)].copy(); Ie["cohort"] = "ext_pooled"; I = pd.concat([I, Ie])
    rows = []; M["intervals"] = {}
    for (det, meth, c), g in I.groupby(["detector", "method", "cohort"]):
        ps = g.groupby("seed").agg(cov=("cov", "mean"), w=("width", "mean"), wmed=("width", "median"),
                                   cov_free=("cov", lambda s: s[g.loc[s.index, "true_burden"] == 0].mean()),
                                   cov_af=("cov", lambda s: s[g.loc[s.index, "true_burden"] > 0].mean()))
        n = int(round(g.groupby("seed").patient.nunique().mean())); k = int(round(ps["cov"].mean() * n))  # patients per seed
        lo, hi = clopper_pearson(k, n)
        M["intervals"][f"{det}|{meth}|{c}"] = dict(coverage=[float(ps["cov"].mean()), float(ps["cov"].std())], cp95=[lo, hi], n=n,
                                                  mean_width_pp=[float(ps.w.mean()), float(ps.w.std())], median_width_pp=[float(ps.wmed.mean()), float(ps.wmed.std())],
                                                  coverage_af_free=float(ps.cov_free.mean()), coverage_af=float(ps.cov_af.mean()))
        if det == cfg_primary:
            rows.append({"Method": meth, "Cohort": c, "n": n, "Coverage (mean ± SD over seeds)": fmt(ps["cov"].mean(), ps["cov"].std(), 3),
                         "Clopper–Pearson 95% CI": f"{lo:.3f}–{hi:.3f}", "Coverage AF-free": f"{ps.cov_free.mean():.3f}",
                         "Coverage AF": f"{ps.cov_af.mean():.3f}", "Mean width (pp)": fmt(ps.w.mean(), ps.w.std()), "Median width (pp)": fmt(ps.wmed.mean(), ps.wmed.std())})
    it = pd.DataFrame(rows); it["o"] = it.Cohort.map({c: i for i, c in enumerate(["calB"] + COH + ["ext_pooled"])}); it = it.sort_values(["Method", "o"]).drop(columns="o")
    md_table(it, os.path.join(tab, "table7_intervals"))

    # ---------------- Ablation ----------------
    abl = [e for e in R.estimator.unique() if e.startswith("PA-HMMQ") or e.startswith("HMM-src")] + ["EMQ", "CC"]
    for det in sorted(R.detector.unique()):
        rows = []
        for est in sorted(set(abl), key=lambda s: (not s.startswith("PA"), s)):
            r = {"Variant": est}
            for c in ["calB", "dev_test"] + EXT + ["ext_pooled"]:
                g = per_seed[(per_seed.detector == det) & (per_seed.estimator == est) & (per_seed.cohort == c)]
                r[c] = fmt(g.mae_pp.mean(), g.mae_pp.std()) if len(g) else "–"
            rows.append(r)
        md_table(pd.DataFrame(rows), os.path.join(tab, "table8_ablation" + ("" if det == cfg_primary else f"_{det}")))
    if os.path.exists(os.path.join(res, "revision_selection.json")):
        sel = json.load(open(os.path.join(res, "revision_selection.json")))
        md_table(pd.DataFrame([{"Seed": k.split("_")[0], "Detector": k.split("_", 1)[1], "Selected emission": v["chosen"],
                                **{f"calA MAE {kk} (pp)": f"{vv:.2f}" for kk, vv in v["calA_mae"].items()}} for k, v in sel.items()]),
                 os.path.join(tab, "table15_R1_emission_selection"))
        S["R1_selection"] = sel

    # ---------------- AF+AFL sensitivity & burden strata & subgroups ----------------
    rows = []; S["afl"] = {}
    for est in BASELINES + ["HMM-src[rawE]", PA_PRE, PA_RAW] + ([PA_SEL] if has_sel else []):
        g = RP[(RP.detector == cfg_primary) & (RP.estimator == est) & (RP.cohort == "ext_pooled")]
        g0 = g[g.afl_burden == 0]
        a, b, c = g.groupby('seed').ae.mean(), g.groupby('seed').ae_afafl.mean(), g0.groupby('seed').ae.mean()
        rows.append({"Estimator": est, "MAE vs AF reference (pp)": fmt(a.mean(), a.std()),
                     "MAE vs AF+AFL reference (pp)": fmt(b.mean(), b.std()),
                     f"MAE excluding patients with any AFL, n={g0.patient.nunique()} (post hoc)": fmt(c.mean(), c.std())})
        S["afl"][est] = dict(mae_af=float(a.mean()), mae_afafl=float(b.mean()), mae_no_afl=float(c.mean()), n_no_afl=int(g0.patient.nunique()),
                             n_with_afl=int(g[g.afl_burden > 0].patient.nunique()))
    md_table(pd.DataFrame(rows), os.path.join(tab, "table14_afl_sensitivity"))
    # post-hoc tests in AF+AFL reference and in patients without AFL
    for label, col, filt in [("afafl_reference", "ae_afafl", None), ("no_afl_patients", "ae", "noafl")]:
        x = RP[(RP.detector == cfg_primary) & (RP.cohort == "ext_pooled")]
        if filt: x = x[x.afl_burden == 0]
        a = x[x.estimator == FINAL].groupby("patient")[col].mean().sort_index()
        res_ = {}
        for b in BASELINES:
            bb = x[x.estimator == b].groupby("patient")[col].mean().loc[a.index]
            res_[b] = paired_wilcoxon(a.values, bb.values, n_boot=2000, seed=0)
        adj = holm({b: v["p"] for b, v in res_.items()})
        for b in res_: res_[b]["p_holm"] = adj[b]
        S["tests"][f"{cfg_primary}|{FINAL}|ext_pooled|{label}"] = res_
    bins = [-0.001, 0, 0.01, 0.10, 0.50, 1.0]; labels = ["0 (AF-free)", "(0,1%]", "(1,10%]", "(10,50%]", ">50%"]
    RP["stratum"] = pd.cut(RP.true_burden, bins, labels=labels)
    rows = []
    for est in ["CC", "CC-MF", "PCC-iso", "ACC", "EMQ", "HMM-src", "HMM-src[rawE]", PA_PRE, PA_RAW] + ([PA_SEL] if has_sel else []):
        g = RP[(RP.detector == cfg_primary) & (RP.estimator == est) & (RP.cohort == "ext_pooled")]
        r = {"Estimator": est}
        for lab in labels:
            gg = g[g.stratum == lab]
            r[f"{lab} (n={gg.patient.nunique()})"] = f"{gg.groupby('seed').ae.mean().mean():.2f}" if len(gg) else "–"
        rows.append(r)
    md_table(pd.DataFrame(rows), os.path.join(tab, "table9_burden_strata"))

    # ---------------- Error analysis (Spearman) ----------------
    g = RP[(RP.detector == cfg_primary) & (RP.estimator == FINAL) & (RP.cohort == "ext_pooled")].groupby("patient").agg(
        ae=("ae", "mean"), err=("err", "mean"), true_burden=("true_burden", "first"), ectopy_sv=("ectopy_sv", "first"),
        ectopy_v=("ectopy_v", "first"), afl=("afl_burden", "first"), hours=("hours", "first"), db=("db", "first"))
    S["error_correlations"] = {}
    for k in ["ectopy_sv", "ectopy_v", "afl", "true_burden", "hours"]:
        rho, p = stats.spearmanr(g[k], g.ae); S["error_correlations"][k] = dict(rho=float(rho), p=float(p))
    worst = g.sort_values("ae", ascending=False).head(15).reset_index()
    worst = worst.assign(**{c: worst[c].map(lambda v: f"{v:.3f}") for c in ["ae", "err", "true_burden", "ectopy_sv", "ectopy_v", "afl", "hours"]})
    md_table(worst, os.path.join(tab, "table10_worst_patients"))

    # ---------------- SHDB-AF demographic subgroups ----------------
    meta = os.path.join("data/raw/shdb-af/AdditionalData.csv")
    if os.path.exists(meta):
        md = pd.read_csv(meta, encoding="utf-8-sig")
        md["patient"] = "shdb_" + md["Subject_ID"].astype(str).str.strip()
        md = md.sort_values("Data_ID").drop_duplicates("patient")[["patient", "Sex", "Age_at_Holter"]]
        md["Sex"] = md.Sex.map({"M": "male", "F": "female"}).fillna(md.Sex)
        rows = []
        for est in ["CC", PA_PRE, PA_RAW]:
            g = RP[(RP.detector == cfg_primary) & (RP.estimator == est) & (RP.cohort == "ext_shdb-af")].merge(md, on="patient", how="left")
            age_med = g.drop_duplicates("patient")["Age_at_Holter"].median()
            for name, mask in [("female", g.Sex.str.lower() == "female"), ("male", g.Sex.str.lower() == "male"),
                               (f"age < {age_med:.0f}", g["Age_at_Holter"] < age_med), (f"age ≥ {age_med:.0f}", g["Age_at_Holter"] >= age_med)]:
                gg = g[mask]
                rows.append({"Estimator": est, "Subgroup": name, "n": gg.patient.nunique(), "MAE (pp)": f"{gg.groupby('seed').ae.mean().mean():.2f}"})
        md_table(pd.DataFrame(rows), os.path.join(tab, "tableS_shdb_subgroups"))

    S["final_method"] = FINAL
    json.dump(M, open(os.path.join(res, "metrics.json"), "w"), indent=1, default=float)
    json.dump(S, open(os.path.join(res, "statistics.json"), "w"), indent=1, default=float)
    print("analysis done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", default="../results"); ap.add_argument("--tables", default="../tables")
    a = ap.parse_args(); main(a.res, a.tables)
