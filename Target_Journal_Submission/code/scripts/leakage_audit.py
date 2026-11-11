"""Phase-8 data-leakage audit.

1. Duplicate / near-duplicate recordings across ALL databases: fingerprint = RR intervals rounded to
   8 ms over 5 windows sampled at fixed positions; any shared fingerprint between two recordings is flagged.
   Also exact duplicate windows (identical 60-RR vectors) across patients.
2. Patient-level split disjointness for every seed (re-derived with the same split function).
3. Development vs external patient-ID disjointness.
4. Summary of preprocessing scope (what is fit on which data).
"""
from __future__ import annotations
import hashlib, json, os, sys
import numpy as np, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.dataset import load, DEV_DBS, EXT_DBS
from src.training.splits import patient_split


def main(out="../results/leakage_audit.json"):
    cfg = yaml.safe_load(open("config/default.yaml"))
    D = load(DEV_DBS + EXT_DBS)
    rep = {}
    # 1) window-level exact duplicates across different patients
    q = np.round(D["rr"] / 0.008).astype(np.int32)
    h = np.array([hashlib.md5(r.tobytes()).hexdigest() for r in q])
    uniq, inv, cnt = np.unique(h, return_inverse=True, return_counts=True)
    dup_groups = np.flatnonzero(cnt > 1)
    cross = 0; examples = []
    for g in dup_groups:
        idx = np.flatnonzero(inv == g)
        pats = set(D["patient"][idx])
        if len(pats) > 1:
            cross += 1
            if len(examples) < 10:
                examples.append(sorted(pats))
    rep["windows_total"] = int(len(h)); rep["duplicate_window_hashes"] = int(len(dup_groups))
    rep["duplicate_windows_shared_across_patients"] = cross; rep["examples_cross_patient"] = examples
    # 2) recording-level fingerprints: 5 windows at fixed relative positions
    rec_fp = {}
    for rec in np.unique(D["record"]):
        idx = np.flatnonzero(D["record"] == rec)
        if len(idx) < 10: continue
        pos = idx[np.linspace(0, len(idx) - 1, 5).astype(int)]
        rec_fp.setdefault("|".join(h[pos]), []).append(rec)
    rep["recordings_fingerprinted"] = int(sum(len(v) for v in rec_fp.values()))
    rep["recording_fingerprint_collisions"] = [v for v in rec_fp.values() if len(v) > 1]
    # 3) split disjointness
    dev = load(DEV_DBS)
    pats, first = np.unique(dev["patient"], return_index=True)
    pdb = dev["db"][first]; has_af = np.array([dev["y"][dev["patient"] == p].any() for p in pats])
    fr = {k: v for k, v in cfg["split"].items() if k != "inner_val_of_train"}
    rep["splits"] = {}
    for s in cfg["seeds"]:
        sp = patient_split(pats, pdb, has_af, fr, s)
        inter = {f"{a}&{b}": len(sp[a] & sp[b]) for a in sp for b in sp if a < b}
        rep["splits"][s] = dict(sizes={k: len(v) for k, v in sp.items()}, overlaps=inter,
                                covers_all=len(set().union(*sp.values())) == len(pats))
    ext_p = set(np.unique(load(EXT_DBS)["patient"]))
    rep["dev_external_patient_overlap"] = len(set(pats) & ext_p)
    rep["preprocessing_scope"] = {
        "features": "computed per window from that window's 60 RR intervals only (no cross-window or global statistics)",
        "RRNet normalisation": "per-window (log RR minus window mean); no dataset-level statistics",
        "Classical-LR scaler": "StandardScaler fit on inner-fit training patients only",
        "early stopping": "inner validation patients (subset of training split)",
        "burden calibration (thresholds, isotonic, emissions, source HMM dynamics)": "calA patients only",
        "conformal quantile": "calB patients only",
        "external cohorts": "never used for training, calibration, tuning or model selection",
        "per-patient EM (EMQ, PA-HMMQ)": "unsupervised: uses only the test patient's own detector outputs, never its labels"}
    json.dump(rep, open(out, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("splits",)}, indent=1, default=str)[:3000])
    print({s: v["overlaps"] for s, v in rep["splits"].items()})


if __name__ == "__main__":
    main(sys.argv[1] + "/leakage_audit.json" if len(sys.argv) > 1 else "../results/leakage_audit.json")
