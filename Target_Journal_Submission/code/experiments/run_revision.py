"""Revision R1 (post hoc, see supplementary S1 §7): per-detector emission selection on calibration-A patients.
Re-uses the saved (seed, detector) models and the identical patient splits of run_main; appends estimators
'HMM-src[sel]' and 'PA-HMMQ[sel]' and the interval 'PA-HMMQ[sel]+conformal(norm)' to separate result files."""
from __future__ import annotations
import argparse, json, os, pickle, sys, time
import numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.dataset import load
from src.training.splits import patient_split
from src.models.burden import estimate, select_emission, true_burden
from src.models.conformal import fit_interval, predict_interval
from experiments.run_main import load_model, patient_table, subset, log


def main(cfg, out, detectors, seeds):
    t0 = time.time()
    W = cfg["window_beats"]
    DEV = load(cfg["dev_dbs"], W=W); EXT = {db: load([db], W=W) for db in cfg["external_dbs"]}
    pats, first = np.unique(DEV["patient"], return_index=True); pdb = DEV["db"][first]
    has_af = np.array([DEV["y"][DEV["patient"] == p].any() for p in pats])
    rows, irows, sel = [], [], {}
    for seed in seeds:
        sp = patient_split(pats, pdb, has_af, {k: v for k, v in cfg["split"].items() if k != "inner_val_of_train"}, seed)
        S = {k: subset(DEV, np.isin(DEV["patient"], sorted(v))) for k, v in sp.items()}
        cohorts = {"calB": S["calB"], "dev_test": S["test"], **{f"ext_{k}": v for k, v in EXT.items()}}
        for det_name in detectors:
            det, cal = load_model(out, seed, det_name)
            cA = S["calA"]; pA = det.predict(cA["X"], cA["rr"])
            scores = select_emission(cal, pA, cA["y"], cA["dur"], cA["seqkey"], cA["patient"], cA["af_frac"])
            sel[f"{seed}_{det_name}"] = dict(chosen=cal.emis_sel_name, calA_mae=scores)
            pickle.dump(cal, open(os.path.join(out, "models", f"seed{seed}_{det_name}_calibrator_R1.pkl"), "wb"))
            ests = {}
            for k, v in cohorts.items():
                p = det.predict(v["X"], v["rr"])
                e, pts, samp = estimate(cal, p, v["dur"], v["seqkey"], v["patient"], ["HMM-src", "PA-HMMQ"],
                                        n_samples=cfg["ffbs_samples"], seed=seed, emission="sel")
                ests[k] = (e, pts, samp.std(0))
            eB, ptsB, sB = ests["calB"]
            tbB, _ = true_burden(S["calB"]["af_frac"], S["calB"]["dur"], S["calB"]["patient"])
            q = fit_interval(tbB, eB["PA-HMMQ"], sB, cfg["alpha"], cfg["eps"])
            sel[f"{seed}_{det_name}"]["conformal_q_norm"] = q
            for k, v in cohorts.items():
                e, pts, sg = ests[k]
                pt = patient_table(v).set_index("patient").loc[pts].reset_index()
                for nm, est in (("HMM-src[sel]", "HMM-src"), ("PA-HMMQ[sel]", "PA-HMMQ")):
                    df = pt.copy(); df["estimate"] = e[est]
                    df["seed"], df["detector"], df["estimator"], df["cohort"] = seed, det_name, nm, k
                    rows.append(df)
                lo, hi = predict_interval(e["PA-HMMQ"], q, sg, cfg["eps"])
                irows.append(pd.DataFrame(dict(seed=seed, detector=det_name, cohort=k, method="PA-HMMQ[sel]+conformal(norm)", patient=pts,
                                               true_burden=pt["true_burden"].values, estimate=e["PA-HMMQ"], lo=lo, hi=hi, sigma=sg, db=pt["db"].values)))
            log(f"R1 seed {seed} {det_name}: selected {cal.emis_sel_name} ({time.time()-t0:.0f}s)")
            pd.concat(rows).to_csv(os.path.join(out, "revision_results.csv"), index=False)
            pd.concat(irows).to_csv(os.path.join(out, "revision_intervals.csv"), index=False)
            json.dump(sel, open(os.path.join(out, "revision_selection.json"), "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", default="config/default.yaml"); ap.add_argument("--out", default="../results")
    ap.add_argument("--detectors", nargs="*", default=["Classical-LR", "LightGBM", "RRNet"]); ap.add_argument("--seeds", nargs="*", type=int)
    a = ap.parse_args(); cfg = yaml.safe_load(open(a.config))
    main(cfg, a.out, a.detectors, a.seeds or cfg["seeds"])
