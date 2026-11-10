"""Build and load cached window-level datasets for every database."""
from __future__ import annotations
import os, sys, time
import numpy as np
from multiprocessing import Pool
from .records import load_database
from ..preprocessing.windows import make_windows
from ..preprocessing.features import rr_features

DEV_DBS = ["ltafdb", "afdb", "mitdb", "nsrdb", "nsr2db", "chfdb"]
EXT_DBS = ["shdb-af", "cpsc2021", "icentia11k"]
ALL_DBS = DEV_DBS + EXT_DBS


def _build_one(args):
    db, raw, out, W = args
    t = time.time()
    recs = load_database(db, raw)
    parts = []
    for ri, r in enumerate(recs):
        w = make_windows(r, W)
        if w is None:
            continue
        n = len(w["y"])
        w["patient"] = np.array([r["patient"]] * n)
        w["record"] = np.array([f"{db}/{r['record']}"] * n)
        # sequence key: windows are temporally ordered within (record, seq)
        w["seqkey"] = np.array([f"{db}/{r['record']}#{s}" for s in w["seq"]])
        parts.append(w)
    D = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    D["X"] = rr_features(D["rr"])
    D["db"] = np.array([db] * len(D["y"]))
    np.savez_compressed(os.path.join(out, f"{db}_W{W}.npz"), **D)
    return f"{db}: windows={len(D['y'])} patients={len(set(D['patient']))} AFwin={D['y'].mean():.3f} ({time.time()-t:.0f}s)"


def build_cache(raw="data/raw", out="data/processed", W=60, dbs=None, procs=4):
    os.makedirs(out, exist_ok=True)
    dbs = dbs or ALL_DBS
    todo = [(d, raw, out, W) for d in dbs if not os.path.exists(os.path.join(out, f"{d}_W{W}.npz"))]
    with Pool(min(procs, max(1, len(todo)))) as p:
        for msg in p.imap_unordered(_build_one, todo):
            print(msg, flush=True)


def load(dbs, out="data/processed", W=60):
    parts = [dict(np.load(os.path.join(out, f"{d}_W{W}.npz"), allow_pickle=False)) for d in dbs]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--W", type=int, default=60); ap.add_argument("--dbs", nargs="*")
    a = ap.parse_args()
    build_cache(W=a.W, dbs=a.dbs)
