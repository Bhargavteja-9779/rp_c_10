"""Post hoc (review round 8, competing-researcher critique): can a longer median filter on hard window labels match
the HMM burden layer? Median-filter lengths k ∈ {3,5,7,9,15} windows (LightGBM, 5 seeds). k is selected on development
patients (calB ∪ dev_test) only; external cohorts are evaluated afterwards."""
import json, os, sys
import numpy as np, pandas as pd, yaml
from scipy.ndimage import median_filter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.dataset import load
from src.training.splits import patient_split
from src.models.burden import true_burden, group_mean, _seq_index
from experiments.run_main import load_model, subset
from experiments.analyze import md_table

KS = [3, 5, 7, 9, 15]


def ccmf(p, d, seqkey, patient, k):
    pats, pidx = np.unique(patient, return_inverse=True); sidx = _seq_index(seqkey)
    h = (p >= 0.5).astype(float); hm = h.copy()
    order = np.argsort(sidx, kind="stable"); s_sorted = sidx[order]
    bounds = np.flatnonzero(np.r_[True, s_sorted[1:] != s_sorted[:-1], True])
    for a, b in zip(bounds[:-1], bounds[1:]):
        ix = order[a:b]
        if len(ix) >= 3: hm[ix] = median_filter(h[ix], size=min(k, len(ix) if len(ix) % 2 else len(ix) - 1), mode="nearest")
    return group_mean(hm, d, pidx, len(pats)), pats


def main(res="../results", tab="../tables"):
    cfg = yaml.safe_load(open("config/default.yaml"))
    DEV = load(cfg["dev_dbs"]); EXT = {db: load([db]) for db in cfg["external_dbs"]}
    pats, first = np.unique(DEV["patient"], return_index=True); pdb = DEV["db"][first]
    has_af = np.array([DEV["y"][DEV["patient"] == p].any() for p in pats])
    rows = []
    for seed in cfg["seeds"]:
        sp = patient_split(pats, pdb, has_af, {k: v for k, v in cfg["split"].items() if k != "inner_val_of_train"}, seed)
        det, _ = load_model(res, seed, "LightGBM")
        cohorts = {"calB": subset(DEV, np.isin(DEV["patient"], sorted(sp["calB"]))), "dev_test": subset(DEV, np.isin(DEV["patient"], sorted(sp["test"]))),
                   **{f"ext_{k}": v for k, v in EXT.items()}}
        for c, v in cohorts.items():
            p = det.predict(v["X"], v["rr"]); tb, tp = true_burden(v["af_frac"], v["dur"], v["patient"])
            for k in KS:
                e, ep = ccmf(p, v["dur"], v["seqkey"], v["patient"], k)
                rows.append(pd.DataFrame(dict(seed=seed, cohort=c, k=k, patient=ep, ae=np.abs(e - tb) * 100)))
        print("seed", seed, "done", flush=True)
    D = pd.concat(rows); D.to_csv(os.path.join(res, "smoother_check.csv"), index=False)
    dev = D[D.cohort.isin(["calB", "dev_test"])].groupby("k").ae.mean(); kbest = int(dev.idxmin())
    R = pd.read_csv(os.path.join(res, "raw_results.csv")); R = R[(R.detector == "LightGBM") & R.cohort.str.startswith("ext_") & (R.estimator == "PA-HMMQ[rawE]")]
    R["ae"] = (R.estimate - R.true_burden).abs() * 100
    ext = D[D.cohort.str.startswith("ext_")]
    out = {"dev_mae_by_k": {int(k): float(v) for k, v in dev.items()}, "k_selected_on_dev": kbest,
           "ext_pooled_mae_by_k": {int(k): float(g.groupby("seed").ae.mean().mean()) for k, g in ext.groupby("k")},
           "ext_pooled_mae_final_pahmmq": float(R.groupby("seed").ae.mean().mean())}
    a = R.groupby("patient").ae.mean(); b = ext[ext.k == kbest].groupby("patient").ae.mean().loc[a.index]
    from src.statistics.tests import paired_wilcoxon
    out["final_vs_best_mf"] = paired_wilcoxon(a.values, b.values)
    md_table(pd.DataFrame([{"Median-filter length (windows)": k, "Development MAE (pp)": f"{out['dev_mae_by_k'][k]:.2f}",
                            "Pooled external MAE (pp)": f"{out['ext_pooled_mae_by_k'][k]:.2f}"} for k in KS]), os.path.join(tab, "table19_median_filter_lengths"))
    S = json.load(open(os.path.join(res, "statistics.json"))); S["smoother_check"] = out
    json.dump(S, open(os.path.join(res, "statistics.json"), "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main(*(sys.argv[1:3]))
