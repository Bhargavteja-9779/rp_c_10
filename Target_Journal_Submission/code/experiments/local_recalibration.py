"""Post-hoc (review round 5): local conformal recalibration in each external cohort.
For each seed and external cohort, n_local labelled patients are drawn at random (200 repeats) to recompute the
normalised conformal quantile for the final PA-HMMQ; coverage and width are evaluated on the remaining patients.
Uses only per-patient estimates and posterior SDs already stored in results/intervals.csv."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.conformal import conformal_quantile
from experiments.analyze import md_table

EPS, ALPHA = 0.002, 0.10


def main(res="../results", tab="../tables", n_locals=(10, 20, 40), reps=200, det="LightGBM", method="PA-HMMQ[rawE]+conformal(norm)"):
    I = pd.read_csv(os.path.join(res, "intervals.csv"))
    I = I[(I.detector == det) & (I.method == method) & I.cohort.str.startswith("ext_")]
    rows, out = [], {}
    rng = np.random.default_rng(2026)
    for coh, gc in I.groupby("cohort"):
        for nl in n_locals:
            cov, wid, cov_af = [], [], []
            for seed, g in gc.groupby("seed"):
                B, Bh, sg = g.true_burden.values, g.estimate.values, g.sigma.values
                for _ in range(reps):
                    idx = rng.permutation(len(B)); loc, ev = idx[:nl], idx[nl:]
                    q = conformal_quantile(np.abs(B[loc] - Bh[loc]) / (sg[loc] + EPS), ALPHA)
                    if not np.isfinite(q): q = np.max(np.abs(B[loc] - Bh[loc]) / (sg[loc] + EPS))
                    lo = np.clip(Bh[ev] - q * (sg[ev] + EPS), 0, 1); hi = np.clip(Bh[ev] + q * (sg[ev] + EPS), 0, 1)
                    c = (B[ev] >= lo - 1e-12) & (B[ev] <= hi + 1e-12)
                    cov.append(c.mean()); wid.append(100 * (hi - lo).mean())
                    if (B[ev] > 0).any(): cov_af.append(c[B[ev] > 0].mean())
            cov, wid = np.array(cov), np.array(wid)
            out[f"{coh}|{nl}"] = dict(mean_cov=float(cov.mean()), p05_cov=float(np.percentile(cov, 5)), p95_cov=float(np.percentile(cov, 95)),
                                     mean_cov_af=float(np.mean(cov_af)), mean_width=float(wid.mean()))
            rows.append({"Cohort": coh, "Local calibration patients": nl, "Coverage, mean": f"{cov.mean():.3f}",
                         "Coverage, 5th–95th percentile": f"{np.percentile(cov, 5):.3f}–{np.percentile(cov, 95):.3f}",
                         "Coverage in AF patients": f"{np.mean(cov_af):.3f}", "Mean width (pp)": f"{wid.mean():.2f}"})
    md_table(pd.DataFrame(rows), os.path.join(tab, "table18_local_recalibration"))
    S = json.load(open(os.path.join(res, "statistics.json"))); S["local_recalibration"] = out
    json.dump(S, open(os.path.join(res, "statistics.json"), "w"), indent=1, default=float)
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    main(*(sys.argv[1:3]))
