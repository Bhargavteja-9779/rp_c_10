"""Experiments 4b and 7b: reduced training data (25%, 50% of training patients) and window length
(30, 120 beats), primary detector (LightGBM), 5 seeds, external cohorts SHDB-AF and CPSC2021
(Icentia11k omitted for compute; documented deviation). Re-uses run_main.run with modified configs."""
import argparse, copy, os, sys
import yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments.run_main import run

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", default="../results"); ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    base = yaml.safe_load(open("config/default.yaml"))
    base.update(external_dbs=["shdb-af", "cpsc2021"], detectors=["LightGBM"], ablations=False)
    variants = {"trainfrac_25": dict(train_fraction=0.25), "trainfrac_50": dict(train_fraction=0.50),
                "window_30": dict(window_beats=30), "window_120": dict(window_beats=120)}
    for name, upd in variants.items():
        if a.only and name not in a.only: continue
        out = os.path.join(a.res, "sensitivity", name)
        if os.path.exists(os.path.join(out, "raw_results.csv")) and len(open(os.path.join(out, "raw_results.csv")).readlines()) > 10:
            done_seeds = set()
            import pandas as pd
            done_seeds = set(pd.read_csv(os.path.join(out, "raw_results.csv")).seed.unique())
            if done_seeds >= set(base["seeds"]):
                print("skip", name); continue
        cfg = copy.deepcopy(base); cfg.update(upd)
        run(cfg, out)
