"""Tables for reduced-training-data, window-length and robustness experiments."""
import argparse, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments.analyze import md_table, fmt
EST = ["CC", "CC-MF", "PCC-iso", "ACC", "EMQ", "HMM-src", "PA-HMMQ", "PA-HMMQ[rawE]"]


def main(res, tab):
    os.makedirs(tab, exist_ok=True)
    rows = []
    base = os.path.join(res, "raw_results.csv")
    variants = [("100% training data, W=60 (main)", base)] + [
        (lab, os.path.join(res, "sensitivity", d, "raw_results.csv")) for lab, d in
        [("25% training data", "trainfrac_25"), ("50% training data", "trainfrac_50"), ("window = 30 beats", "window_30"), ("window = 120 beats", "window_120")]]
    for lab, p in variants:
        if not os.path.exists(p): continue
        R = pd.read_csv(p); R = R[(R.detector == "LightGBM") & R.cohort.isin(["dev_test", "ext_shdb-af", "ext_cpsc2021"])]
        R["ae"] = (R.estimate - R.true_burden).abs() * 100
        for est in EST:
            r = {"Setting": lab, "Estimator": est}
            for c in ["dev_test", "ext_shdb-af", "ext_cpsc2021"]:
                g = R[(R.estimator == est) & (R.cohort == c)].groupby("seed").ae.mean()
                r[c] = fmt(g.mean(), g.std()) if len(g) else "–"
            rows.append(r)
    if rows:
        md_table(pd.DataFrame(rows), os.path.join(tab, "table11_sensitivity_trainfrac_window"))
    p = os.path.join(res, "robustness_results.csv")
    if os.path.exists(p):
        X = pd.read_csv(p); X["ae"] = (X.estimate - X.true_burden).abs() * 100
        rows = []
        for det in X.detector.unique():
            for cond in dict.fromkeys(X.condition):
                r = {"Detector": det, "Condition": cond}
                for est in EST:
                    g = X[(X.detector == det) & (X.condition == cond) & (X.estimator == est)].groupby("seed").ae.mean()
                    r[est] = fmt(g.mean(), g.std()) if len(g) else "–"
                rows.append(r)
        md_table(pd.DataFrame(rows), os.path.join(tab, "table12_robustness"))
        I = pd.read_csv(os.path.join(res, "robustness_intervals.csv"))
        I["cov"] = (I.true_burden >= I.lo - 1e-12) & (I.true_burden <= I.hi + 1e-12); I["w"] = (I.hi - I.lo) * 100
        rows = []
        for (det, m, cond), g in I.groupby(["detector", "method", "condition"], sort=False):
            s = g.groupby("seed").agg(c=("cov", "mean"), w=("w", "mean"))
            rows.append({"Detector": det, "Method": m, "Condition": cond, "Coverage": fmt(s.c.mean(), s.c.std(), 3), "Mean width (pp)": fmt(s.w.mean(), s.w.std())})
        md_table(pd.DataFrame(rows), os.path.join(tab, "table13_robustness_intervals"))
    print("sensitivity tables done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", default="../results"); ap.add_argument("--tables", default="../tables")
    a = ap.parse_args(); main(a.res, a.tables)
