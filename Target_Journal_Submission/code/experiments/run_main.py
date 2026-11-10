"""Experiments 1, 2, 3, 5 and 7 (window-length excluded): train detectors per seed, estimate
per-patient AF burden with every estimator, conformal intervals, ablations.

Outputs (in --out):
  raw_results.csv        one row per (seed, detector, estimator, split/cohort, patient)
  window_metrics.csv     window-level detector metrics per (seed, detector, cohort)
  intervals.csv          per-patient intervals for interval methods
  training_history.csv   RRNet learning curves
  calibration_stats.json per seed/detector source-calibration quantities
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.dataset import load
from src.training.splits import patient_split
from src.models.detectors import DETECTORS, get_device
from src.models.burden import BurdenCalibrator, estimate, true_burden, ESTIMATORS, group_mean
from src.models.hmm import BurdenHMM
from src.models.conformal import fit_interval, predict_interval
from src.evaluation.metrics import window_metrics, curves


def log(msg, fh=None):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if fh: fh.write(line + "\n"); fh.flush()


def subset(D, mask):
    return {k: v[mask] for k, v in D.items()}


def patient_table(D):
    """Per-patient covariates used in error analysis."""
    pats, pidx = np.unique(D["patient"], return_inverse=True)
    n = len(pats); d = D["dur"]
    return pd.DataFrame(dict(
        patient=pats,
        hours=np.bincount(pidx, weights=d, minlength=n) / 3600,
        n_windows=np.bincount(pidx, minlength=n),
        true_burden=group_mean(D["af_frac"], d, pidx, n),
        true_burden_af_afl=group_mean(np.clip(D["af_frac"] + D["afl_frac"], 0, 1), d, pidx, n),
        afl_burden=group_mean(D["afl_frac"], d, pidx, n),
        ectopy_sv=group_mean(D["ect_sv"], d, pidx, n), ectopy_v=group_mean(D["ect_v"], d, pidx, n),
        unclassified=group_mean(D["unk"], d, pidx, n),
        db=[D["db"][pidx == i][0] for i in range(n)]))


def run(cfg, out, detectors=None, seeds=None):
    os.makedirs(out, exist_ok=True)
    fh = open(os.path.join(out, "experiment_logs_main.log"), "a")
    log(f"device={get_device()} torch threads={__import__('torch').get_num_threads()}", fh)
    W = cfg["window_beats"]
    DEV = load(cfg["dev_dbs"], W=W)
    EXT = {}
    for db in cfg["external_dbs"]:
        E = load([db], W=W)
        lim = cfg.get("external_patient_limit")
        if lim:
            keep = sorted(np.unique(E["patient"]))[:lim]
            E = subset(E, np.isin(E["patient"], keep))
        EXT[db] = E
    log(f"dev windows={len(DEV['y'])} patients={len(np.unique(DEV['patient']))}; " +
        "; ".join(f"{k}: windows={len(v['y'])} patients={len(np.unique(v['patient']))}" for k, v in EXT.items()), fh)
    # patient-level stratification variables
    pats, first = np.unique(DEV["patient"], return_index=True)
    pdb = DEV["db"][first]
    has_af = np.array([DEV["y"][DEV["patient"] == p].any() for p in pats])
    rows, wrows, irows, hist, calstats, crows, relrows = [], [], [], [], {}, [], []
    detectors = detectors or cfg["detectors"]
    for seed in (seeds or cfg["seeds"]):
        sp = patient_split(pats, pdb, has_af, {k: v for k, v in cfg["split"].items() if k != "inner_val_of_train"}, seed)
        # inner validation patients (subset of train), stratified the same way
        trp = sorted(sp["train"]); tm = np.isin(pats, trp)
        inner = patient_split(pats[tm], pdb[tm], has_af[tm],
                              {"fit": 1 - cfg["split"]["inner_val_of_train"], "val": cfg["split"]["inner_val_of_train"]}, seed + 1)
        assert not (set().union(*[sp[a] & sp[b] for a in sp for b in sp if a < b])), "patient leakage across splits"
        frac = cfg.get("train_fraction", 1.0)
        if frac < 1.0:  # reduced training data (Exp 4): stratified subsample of the inner-fit patients
            fp = np.array(sorted(inner["fit"])); fm = np.isin(pats, fp)
            inner["fit"] = patient_split(pats[fm], pdb[fm], has_af[fm], {"keep": frac, "drop": 1 - frac}, seed + 2)["keep"]
        S = {k: subset(DEV, np.isin(DEV["patient"], sorted(v))) for k, v in sp.items()}
        Sfit = subset(DEV, np.isin(DEV["patient"], sorted(inner["fit"])))
        Sval = subset(DEV, np.isin(DEV["patient"], sorted(inner["val"])))
        log(f"seed {seed}: " + ", ".join(f"{k}={len(v)} pts" for k, v in sp.items()) + f" | inner fit={len(inner['fit'])} val={len(inner['val'])}", fh)
        cohorts = {"dev_test": S["test"], **{f"ext_{k}": v for k, v in EXT.items()}}
        for det_name in detectors:
            t0 = time.time()
            Det = DETECTORS[det_name]
            kw = {}
            if det_name == "RRNet":
                kw = dict(epochs=cfg["rrnet"]["epochs"], batch=cfg["rrnet"]["batch"], lr=cfg["rrnet"]["lr"],
                          patience=cfg["rrnet"]["patience"], log=lambda m: log(m, fh))
            if det_name == "LightGBM":
                kw = dict(n_estimators=cfg["lightgbm"]["n_estimators"])
            det = Det(seed=seed, **kw).fit(Sfit["X"], Sfit["rr"], Sfit["y"], Sval["X"], Sval["rr"], Sval["y"])
            if det_name == "RRNet":
                for h in det.history: hist.append(dict(seed=seed, **h))
            train_time = time.time() - t0
            # predictions
            P = {k: det.predict(v["X"], v["rr"]) for k, v in {"calA": S["calA"], "calB": S["calB"], **cohorts}.items()}
            log(f"seed {seed} {det_name}: trained in {train_time:.0f}s, params={det.n_params()}", fh)
            for k, v in cohorts.items():
                wrows.append(dict(seed=seed, detector=det_name, cohort=k, **window_metrics(v["y"], P[k])))
                c = curves(v["y"], P[k])
                if c is not None:
                    crows.append(pd.DataFrame(dict(seed=seed, detector=det_name, cohort=k, curve="roc", x=c["roc_fpr"], y=c["roc_tpr"])))
                    crows.append(pd.DataFrame(dict(seed=seed, detector=det_name, cohort=k, curve="pr", x=c["pr_recall"], y=c["pr_precision"])))
                # reliability diagram data (10 bins)
                b = np.clip((P[k] * 10).astype(int), 0, 9)
                for bi in range(10):
                    m = b == bi
                    if m.any():
                        relrows.append(dict(seed=seed, detector=det_name, cohort=k, bin=bi, mean_p=float(P[k][m].mean()), frac_pos=float(v["y"][m].mean()), n=int(m.sum())))
            # source calibration on calA only
            cA = S["calA"]
            seqA = np.unique(cA["seqkey"], return_inverse=True)[1]
            # seqA must preserve within-sequence order: windows are stored in temporal order per record
            cal = BurdenCalibrator(thr=cfg["threshold"], kappa=cfg["kappa"], bins=cfg["emission_bins"]).fit(
                P["calA"], cA["y"].astype(int), cA["dur"], _ordered_seq(cA["seqkey"]))
            _save_model(out, seed, det_name, det, cal)
            calstats[f"{seed}_{det_name}"] = dict(tpr=cal.tpr, fpr=cal.fpr, m1=cal.m1, m0=cal.m0, prior=cal.prior,
                                                  A_src=cal.hmm_src.A_src.tolist(), pi_src=cal.hmm_src.pi_src.tolist())
            ests = {}
            for k, v in {"calB": S["calB"], **cohorts}.items():
                e, pts, samp = estimate(cal, P[k], v["dur"], v["seqkey"], v["patient"], ESTIMATORS,
                                        n_samples=cfg["ffbs_samples"], seed=seed)
                # ablations: raw-score emissions and kappa grid
                e.update(_ablations(cal, cfg, P[k], v))
                sig = samp.std(0) if samp is not None else None
                lo_cr, hi_cr = (np.quantile(samp, cfg["alpha"] / 2, 0), np.quantile(samp, 1 - cfg["alpha"] / 2, 0)) if samp is not None else (None, None)
                ests[k] = (e, pts, sig, lo_cr, hi_cr)
            # conformal calibration on calB (true burden known there)
            eB, ptsB, sigB, _, _ = ests["calB"]
            tb_B, _ = true_burden(S["calB"]["af_frac"], S["calB"]["dur"], S["calB"]["patient"])
            q = dict(norm=fit_interval(tb_B, eB["PA-HMMQ"], sigB, cfg["alpha"], cfg["eps"]),
                     const_pa=fit_interval(tb_B, eB["PA-HMMQ"], None, cfg["alpha"]),
                     const_cc=fit_interval(tb_B, eB["CC"], None, cfg["alpha"]),
                     const_pcciso=fit_interval(tb_B, eB["PCC-iso"], None, cfg["alpha"]))
            calstats[f"{seed}_{det_name}"]["conformal_q"] = q
            for k, v in {"calB": S["calB"], **cohorts}.items():
                e, pts, sig, lo_cr, hi_cr = ests[k]
                pt = patient_table(v).set_index("patient").loc[pts].reset_index()
                for est_name, bh in e.items():
                    df = pt.copy(); df["estimate"] = bh
                    df["seed"], df["detector"], df["estimator"], df["cohort"] = seed, det_name, est_name, k
                    rows.append(df)
                ivs = {"PA-HMMQ+conformal(norm)": ("PA-HMMQ",) + predict_interval(e["PA-HMMQ"], q["norm"], sig, cfg["eps"]),
                       "PA-HMMQ+conformal(const)": ("PA-HMMQ",) + predict_interval(e["PA-HMMQ"], q["const_pa"]),
                       "CC+conformal(const)": ("CC",) + predict_interval(e["CC"], q["const_cc"]),
                       "PCC-iso+conformal(const)": ("PCC-iso",) + predict_interval(e["PCC-iso"], q["const_pcciso"]),
                       "PA-HMMQ posterior 90% CrI": ("PA-HMMQ", lo_cr, hi_cr)}
                for iv_name, (base, lo, hi) in ivs.items():
                    irows.append(pd.DataFrame(dict(seed=seed, detector=det_name, cohort=k, method=iv_name, patient=pts,
                                                   true_burden=pt["true_burden"].values, estimate=e[base], lo=lo, hi=hi,
                                                   sigma=sig, db=pt["db"].values)))
            log(f"seed {seed} {det_name}: burden + intervals done ({time.time()-t0:.0f}s total)", fh)
            # incremental save (crash safety)
            pd.concat(rows).to_csv(os.path.join(out, "raw_results.csv"), index=False)
            pd.DataFrame(wrows).to_csv(os.path.join(out, "window_metrics.csv"), index=False)
            pd.concat(irows).to_csv(os.path.join(out, "intervals.csv"), index=False)
            pd.DataFrame(hist).to_csv(os.path.join(out, "training_history.csv"), index=False)
            pd.concat(crows).to_csv(os.path.join(out, "curves.csv"), index=False)
            pd.DataFrame(relrows).to_csv(os.path.join(out, "reliability.csv"), index=False)
            json.dump(calstats, open(os.path.join(out, "calibration_stats.json"), "w"), indent=1, default=float)
    fh.close()


def _save_model(out, seed, det_name, det, cal):
    import pickle, torch
    d = os.path.join(out, "models"); os.makedirs(d, exist_ok=True)
    if det_name == "RRNet":
        torch.save(det.net.state_dict(), os.path.join(d, f"seed{seed}_{det_name}.pt"))
        log_ = det.log; det.log = None; net = det.net; det.net = None
        pickle.dump(det, open(os.path.join(d, f"seed{seed}_{det_name}.pkl"), "wb")); det.net = net; det.log = log_
    else:
        pickle.dump(det, open(os.path.join(d, f"seed{seed}_{det_name}.pkl"), "wb"))
    pickle.dump(cal, open(os.path.join(d, f"seed{seed}_{det_name}_calibrator.pkl"), "wb"))


def load_model(out, seed, det_name):
    import pickle, torch
    from src.models.detectors import _RRNetModule
    d = os.path.join(out, "models")
    det = pickle.load(open(os.path.join(d, f"seed{seed}_{det_name}.pkl"), "rb"))
    if det_name == "RRNet":
        det.net = _RRNetModule(); det.net.load_state_dict(torch.load(os.path.join(d, f"seed{seed}_{det_name}.pt"))); det.dev = get_device(); det.net.to(det.dev)
    cal = pickle.load(open(os.path.join(d, f"seed{seed}_{det_name}_calibrator.pkl"), "rb"))
    return det, cal


def _ordered_seq(seqkey):
    from src.models.burden import _seq_index
    return _seq_index(seqkey)


def _ablations(cal, cfg, p, v):
    from src.models.burden import _seq_index
    pats, pidx = np.unique(v["patient"], return_inverse=True); P = len(pats)
    sidx = _seq_index(v["seqkey"]); pos = np.zeros(sidx.max() + 1, dtype=np.int64); pos[sidx] = pidx
    out = {}
    # (a) raw-score emissions: likelihood proportional to (1-p, p) — no source calibration of emissions
    Eraw = np.stack([1 - np.clip(p, 1e-6, 1 - 1e-6), np.clip(p, 1e-6, 1 - 1e-6)], 1)
    g, _ = cal.hmm_pa.infer(Eraw, sidx, pos, P)
    out["PA-HMMQ[rawE]"] = group_mean(g, v["dur"], pidx, P)
    # (b) prior strength grid
    E = cal.emis(p)
    for k in cfg["kappa_grid"]:
        h = BurdenHMM(kappa=float(k)); h.A_src, h.pi_src = cal.hmm_pa.A_src, cal.hmm_pa.pi_src
        g, _ = h.infer(E, sidx, pos, P)
        out[f"PA-HMMQ[k={k}]"] = group_mean(g, v["dur"], pidx, P)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/default.yaml")
    ap.add_argument("--out", default="../results")
    ap.add_argument("--detectors", nargs="*")
    ap.add_argument("--seeds", nargs="*", type=int)
    a = ap.parse_args()
    run(yaml.safe_load(open(a.config)), a.out, a.detectors, a.seeds)
