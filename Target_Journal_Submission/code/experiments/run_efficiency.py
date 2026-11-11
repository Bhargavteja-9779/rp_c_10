"""Experiment 6: computational cost per 24-h recording on the current CPU.
Measures wall-clock time (median of repeats) for each pipeline component on real 24-h
SHDB-AF recordings, parameter counts, and peak Python memory (tracemalloc) of the burden layer."""
from __future__ import annotations
import argparse, json, os, platform, sys, time, tracemalloc
import numpy as np, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
from src.data.dataset import load
from src.preprocessing.features import rr_features
from src.models.burden import estimate
from experiments.run_main import load_model


def timeit(fn, reps=5):
    ts = []
    for _ in range(reps):
        t = time.perf_counter(); fn(); ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def main(res, cfg, seed=11, n_rec=5):
    D = load(["shdb-af"])
    recs = [r for r in np.unique(D["record"])][:n_rec]
    out = {"cpu": platform.processor() or platform.machine(), "torch_threads": torch.get_num_threads(),
           "python": platform.python_version(), "components": {}, "params": {}}
    per = {}
    for rec in recs:
        m = D["record"] == rec
        sub = {k: v[m] for k, v in D.items()}
        hours = sub["dur"].sum() / 3600
        f = 24.0 / hours
        per.setdefault("RR features (16, per window)", []).append(timeit(lambda: rr_features(sub["rr"]), 3) * f)
        for det_name in ["Classical-LR", "LightGBM", "RRNet"]:
            det, cal = load_model(res, seed, det_name)
            out["params"][det_name] = det.n_params()
            per.setdefault(f"{det_name} inference", []).append(timeit(lambda: det.predict(sub["X"], sub["rr"]), 3) * f)
            if det_name == "LightGBM":
                p = det.predict(sub["X"], sub["rr"])
                for est in ["CC", "ACC", "EMQ", "HMM-src", "PA-HMMQ"]:
                    per.setdefault(f"burden: {est}", []).append(timeit(lambda: estimate(cal, p, sub["dur"], sub["seqkey"], sub["patient"], [est], n_samples=0), 3) * f)
                per.setdefault("burden: PA-HMMQ (probability emissions)", []).append(
                    timeit(lambda: estimate(cal, p, sub["dur"], sub["seqkey"], sub["patient"], ["PA-HMMQ"], n_samples=0, raw_emission=True), 3) * f)
                per.setdefault("PA-HMMQ + 200 FFBS samples (for interval)", []).append(
                    timeit(lambda: estimate(cal, p, sub["dur"], sub["seqkey"], sub["patient"], ["PA-HMMQ"], n_samples=cfg["ffbs_samples"], raw_emission=True), 2) * f)
                tracemalloc.start()
                estimate(cal, p, sub["dur"], sub["seqkey"], sub["patient"], ["PA-HMMQ"], n_samples=cfg["ffbs_samples"], raw_emission=True)
                _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
                per.setdefault("_peak_mem_MB_PA-HMMQ+FFBS", []).append(peak / 1e6 * f)
    for k, v in per.items():
        if k.startswith("_"):
            out[k[1:]] = float(np.median(v))
        else:
            out["components"][k] = dict(seconds_per_24h_median=float(np.median(v)), seconds_per_24h_iqr=[float(np.percentile(v, 25)), float(np.percentile(v, 75))])
    out["n_recordings"] = len(recs)
    json.dump(out, open(os.path.join(res, "efficiency.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", default="../results"); ap.add_argument("--config", default="config/default.yaml")
    a = ap.parse_args(); main(a.res, yaml.safe_load(open(a.config)))
