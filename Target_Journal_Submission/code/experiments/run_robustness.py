"""Experiment 4 (robustness): apply simulated R-peak/RR perturbations to the SHDB-AF external cohort and
re-evaluate every saved (seed, detector) model with the main burden estimators and conformal intervals."""
from __future__ import annotations
import argparse, json, os, pickle, sys, time
import numpy as np, pandas as pd, yaml
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.records import load_database
from src.preprocessing.windows import make_windows
from src.preprocessing.features import rr_features
from src.preprocessing.perturb import perturb_record
from src.models.burden import estimate, true_burden
from src.models.conformal import predict_interval
from experiments.run_main import load_model, patient_table

CONDITIONS = [("none", 0.0), ("missed", 0.02), ("missed", 0.05), ("false", 0.02), ("false", 0.05),
              ("jitter", 0.010), ("jitter", 0.025), ("ectopy", 0.05), ("ectopy", 0.10)]
EST = ["CC", "CC-MF", "PCC-iso", "ACC", "EMQ", "HMM-src", "PA-HMMQ"]


def build(args):
    recs, kind, level, W, ci = args
    rng = np.random.default_rng(1000 + ci)
    parts = []
    for r in recs:
        w = make_windows(perturb_record(r, kind, level, rng), W)
        if w is None: continue
        n = len(w["y"])
        w["patient"] = np.array([r["patient"]] * n); w["seqkey"] = np.array([f"{r['record']}#{s}" for s in w["seq"]])
        w["db"] = np.array([r["db"]] * n)
        parts.append(w)
    D = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    D["X"] = rr_features(D["rr"])
    return f"{kind}_{level}", D


def main(cfg, out, db, detectors, seeds, procs):
    t0 = time.time()
    cache = f"data/processed/{db}_records.pkl"
    if os.path.exists(cache):
        recs = pickle.load(open(cache, "rb"))
    else:
        recs = load_database(db, "data/raw"); pickle.dump(recs, open(cache, "wb"))
    with Pool(procs) as p:
        data = dict(p.map(build, [(recs, k, l, cfg["window_beats"], i) for i, (k, l) in enumerate(CONDITIONS)]))
    print(f"perturbed datasets built in {time.time()-t0:.0f}s", flush=True)
    cstats = json.load(open(os.path.join(out, "calibration_stats.json")))
    rows, irows = [], []
    for seed in seeds:
        for det_name in detectors:
            det, cal = load_model(out, seed, det_name)
            q = cstats[f"{seed}_{det_name}"]["conformal_q"]
            for cond, D in data.items():
                p = det.predict(D["X"], D["rr"])
                e, pts, samp = estimate(cal, p, D["dur"], D["seqkey"], D["patient"], EST, n_samples=cfg["ffbs_samples"], seed=seed)
                pt = patient_table(D).set_index("patient").loc[pts].reset_index()
                for est_name, bh in e.items():
                    df = pt[["patient", "true_burden", "hours", "db"]].copy(); df["estimate"] = bh
                    df["seed"], df["detector"], df["estimator"], df["condition"] = seed, det_name, est_name, cond
                    rows.append(df)
                sig = samp.std(0)
                lo, hi = predict_interval(e["PA-HMMQ"], q["norm"], sig, cfg["eps"])
                irows.append(pd.DataFrame(dict(seed=seed, detector=det_name, condition=cond, patient=pts,
                                               true_burden=pt["true_burden"].values, lo=lo, hi=hi)))
            print(f"seed {seed} {det_name} done ({time.time()-t0:.0f}s)", flush=True)
            pd.concat(rows).to_csv(os.path.join(out, "robustness_results.csv"), index=False)
            pd.concat(irows).to_csv(os.path.join(out, "robustness_intervals.csv"), index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml"); ap.add_argument("--out", default="../results")
    ap.add_argument("--db", default="shdb-af"); ap.add_argument("--detectors", nargs="*", default=["LightGBM", "RRNet"])
    ap.add_argument("--seeds", nargs="*", type=int); ap.add_argument("--procs", type=int, default=3)
    a = ap.parse_args(); cfg = yaml.safe_load(open(a.config))
    main(cfg, a.out, a.db, a.detectors, a.seeds or cfg["seeds"], a.procs)
