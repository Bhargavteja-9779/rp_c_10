"""Per-database descriptive summary from the window caches (feeds Table S1 and manuscript tokens)."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.dataset import load, DEV_DBS, EXT_DBS
from src.models.burden import group_mean

INFO = {"ltafdb": ("Long-Term AF Database", "USA", "PhysioNet ltafdb 1.0.0", "ODC-By 1.0"),
        "afdb": ("MIT-BIH AF Database", "USA", "PhysioNet afdb 1.0.0", "ODC-By 1.0"),
        "mitdb": ("MIT-BIH Arrhythmia Database", "USA", "PhysioNet mitdb 1.0.0", "ODC-By 1.0"),
        "nsrdb": ("MIT-BIH Normal Sinus Rhythm Database", "USA", "PhysioNet nsrdb 1.0.0", "ODC-By 1.0"),
        "nsr2db": ("Normal Sinus Rhythm RR Interval Database", "USA", "PhysioNet nsr2db 1.0.0", "ODC-By 1.0"),
        "chfdb": ("BIDMC Congestive Heart Failure Database", "USA", "PhysioNet chfdb 1.0.0", "ODC-By 1.0"),
        "shdb-af": ("SHDB-AF Japanese Holter AF database", "Japan", "PhysioNet shdb-af 1.0.1", "ODC-By 1.0"),
        "cpsc2021": ("4th China Physiological Signal Challenge 2021", "China", "PhysioNet cpsc2021 1.0.0", "CC BY 4.0"),
        "icentia11k": ("Icentia11k continuous ECG (random subset)", "Canada", "PhysioNet icentia11k-continuous-ecg 1.0", "CC BY-NC-SA 4.0")}


def main(out="../results/dataset_summary.json", tab="../tables"):
    rows, S = [], {}
    for db in DEV_DBS + EXT_DBS:
        D = load([db]); pats, pidx = np.unique(D["patient"], return_inverse=True); n = len(pats)
        tb = group_mean(D["af_frac"], D["dur"], pidx, n); afl = group_mean(D["afl_frac"], D["dur"], pidx, n)
        hrs = np.bincount(pidx, weights=D["dur"], minlength=n) / 3600
        S[db] = dict(patients=int(n), recordings=int(len(np.unique(D["record"]))), windows=int(len(D["y"])), hours=float(hrs.sum()),
                     patients_af=int((tb > 0).sum()), patients_afl=int((afl > 0).sum()), af_window_fraction=float(D["y"].mean()),
                     median_hours=float(np.median(hrs)))
        nm, ctry, src, lic = INFO[db]
        rows.append({"Database": nm, "Role": "development" if db in DEV_DBS else "external validation", "Country": ctry, "Source/version": src,
                     "Licence": lic, "Recordings": S[db]["recordings"], "Patients": n, "Hours analysed": f"{hrs.sum():.0f}",
                     "Windows (60 beats)": len(D["y"]), "Patients with AF": S[db]["patients_af"], "Patients with AFL": S[db]["patients_afl"],
                     "AF windows (%)": f"{100*D['y'].mean():.1f}"})
    S["dev_total"] = {k: int(sum(S[d][k] for d in DEV_DBS)) if k != "hours" else float(sum(S[d]["hours"] for d in DEV_DBS)) for k in ["patients", "recordings", "windows", "hours", "patients_af"]}
    S["ext_total"] = {k: int(sum(S[d][k] for d in EXT_DBS)) if k != "hours" else float(sum(S[d]["hours"] for d in EXT_DBS)) for k in ["patients", "recordings", "windows", "hours", "patients_af", "patients_afl"]}
    S["icentia_sampled"] = len(open("data/raw/icentia11k/SAMPLED_PATIENTS").read().split())
    json.dump(S, open(out, "w"), indent=1)
    from experiments.analyze import md_table
    md_table(pd.DataFrame(rows), os.path.join(tab, "tableS1_databases"))
    print(json.dumps({k: S[k] for k in ["dev_total", "ext_total", "icentia_sampled"]}))


if __name__ == "__main__":
    main()
