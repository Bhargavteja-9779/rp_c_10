#!/usr/bin/env python3
"""One-command reproduction.

  python run_all.py --mode quick   # pipeline verification (~15-25 min CPU): 1 seed, reduced epochs,
                                   # 40-patient external subsets; writes to ../results_quick, ../figures_quick, ../tables_quick
  python run_all.py --mode full    # complete study as reported (several hours on a 4-core CPU)

Steps: download annotations -> build window caches -> leakage audit -> main experiments ->
robustness -> reduced training data -> window-length sensitivity -> efficiency -> analysis
(tables, statistics) -> figures. Each step skips work whose outputs already exist unless --force.
"""
import argparse, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(cmd):
    print(f"\n$ {cmd}", flush=True)
    t = time.time(); r = subprocess.run(cmd, shell=True, cwd=HERE)
    if r.returncode != 0:
        sys.exit(f"step failed ({r.returncode}): {cmd}")
    print(f"  done in {time.time()-t:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--skip-download", action="store_true")
    a = ap.parse_args()
    q = a.mode == "quick"
    res = "../results_quick" if q else "../results"; fig = "../figures_quick" if q else "../figures"; tab = "../tables_quick" if q else "../tables"
    cfg = "config/quick.yaml" if q else "config/default.yaml"
    os.makedirs(os.path.join(HERE, res, "experiment_logs"), exist_ok=True)
    if not a.skip_download:
        sh("python -m src.data.download --root data/raw" + (" --icentia-patients 800 --icentia-segments 10" if not q else " --icentia-patients 800 --icentia-segments 10"))
    sh("python -m src.data.dataset --W 60")
    sh("python scripts/leakage_audit.py")
    if a.force or not os.path.exists(os.path.join(HERE, res, "raw_results.csv")):
        sh(f"python experiments/run_main.py --config {cfg} --out {res}")
    if a.force or not os.path.exists(os.path.join(HERE, res, "robustness_results.csv")):
        sh(f"python experiments/run_robustness.py --config {cfg} --out {res}" + (" --seeds 11" if q else ""))
    if not q:
        sh("python experiments/run_sensitivity.py --res ../results")
    sh(f"python experiments/run_efficiency.py --res {res} --config {cfg}")
    sh(f"python experiments/analyze.py --res {res} --tables {tab}")
    sh(f"python experiments/summarize_sensitivity.py --res {res} --tables {tab}")
    sh(f"python -m src.visualization.figures --res {res} --out {fig}")
    sh("python -m pytest -q tests")
    print("\nAll steps completed.")


if __name__ == "__main__":
    main()
