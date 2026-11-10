"""Download annotation (not signal) files from PhysioNet for all databases used.

Only beat/rhythm annotation files and headers are needed because the study works
on RR-interval series. Files are verified against PhysioNet SHA256SUMS where
available. Usage: python -m src.data.download --root data/raw [--icentia-patients 800]
"""
from __future__ import annotations
import argparse, hashlib, os, random, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://physionet.org/files"
# database -> (version path, list of extensions to fetch, records file)
DBS = {
    "ltafdb": ("ltafdb/1.0.0", ["atr", "hea"], "RECORDS"),
    "afdb": ("afdb/1.0.0", ["atr", "qrs", "hea"], "RECORDS"),
    "mitdb": ("mitdb/1.0.0", ["atr", "hea"], "RECORDS"),
    "nsrdb": ("nsrdb/1.0.0", ["atr", "hea"], "RECORDS"),
    "nsr2db": ("nsr2db/1.0.0", ["ecg", "hea"], "RECORDS"),
    "chfdb": ("chfdb/1.0.0", ["ecg", "hea"], "RECORDS"),
    "shdb-af": ("shdb-af/1.0.1", ["atr", "qrs", "hea"], "RECORDS.txt"),
    "cpsc2021": ("cpsc2021/1.0.0", ["atr", "hea"], "RECORDS"),
}
EXTRA = {"shdb-af": ["AdditionalData.csv", "LICENSE.txt"], "cpsc2021": ["LICENSE.txt"],
         "icentia11k": ["LICENSE.txt"]}
ICENTIA = "icentia11k-continuous-ecg/1.0"
UA = {"User-Agent": "af-burden-research/1.0 (python urllib)"}


def fetch(url: str, dest: str, tries: int = 6) -> bool:
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                data = r.read()
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            return True
        except Exception as e:  # network hiccup or 404
            if "404" in str(e):
                return False
            time.sleep(min(2 ** t, 30))
    return False


def sha_table(dbpath: str, root: str) -> dict:
    dest = os.path.join(root, "_sha", dbpath.replace("/", "_") + ".txt")
    if not fetch(f"{BASE}/{dbpath}/SHA256SUMS.txt", dest):
        return {}
    tab = {}
    for line in open(dest):
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            tab[parts[1].lstrip("*")] = parts[0]
    return tab


def verify(path: str, expected: str | None) -> bool:
    if expected is None:
        return True
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return h == expected


def download_db(name: str, root: str, workers: int = 16) -> None:
    dbpath, exts, recfile = DBS[name]
    out = os.path.join(root, name)
    os.makedirs(out, exist_ok=True)
    fetch(f"{BASE}/{dbpath}/{recfile}", os.path.join(out, "RECORDS"))
    recs = [r.strip() for r in open(os.path.join(out, "RECORDS")) if r.strip()]
    sha = sha_table(dbpath, root)
    jobs = [(f"{BASE}/{dbpath}/{r}.{e}", os.path.join(out, f"{r}.{e}"), f"{r}.{e}") for r in recs for e in exts]
    jobs += [(f"{BASE}/{dbpath}/{x}", os.path.join(out, x), x) for x in EXTRA.get(name, [])]
    with ThreadPoolExecutor(workers) as ex:
        ok = list(ex.map(lambda j: fetch(j[0], j[1]), jobs))
    bad = [j[2] for j, o in zip(jobs, ok) if o and not verify(j[1], sha.get(j[2]))]
    missing = [j[2] for j, o in zip(jobs, ok) if not o]
    print(f"[{name}] records={len(recs)} files={len(jobs)} missing={len(missing)} sha_mismatch={len(bad)}", flush=True)
    if missing:
        print(f"  missing (first 10): {missing[:10]}")
    if bad:
        print(f"  SHA mismatch: {bad[:10]}")


def download_icentia(root: str, n_patients: int, n_segments: int, seed: int, workers: int = 24) -> None:
    """Random (seeded) subset of Icentia11k patients; first `n_segments` segments each.
    Patients are sampled uniformly at random WITHOUT looking at labels (no AF enrichment)."""
    out = os.path.join(root, "icentia11k")
    os.makedirs(out, exist_ok=True)
    rng = random.Random(seed)
    pids = sorted(rng.sample(range(11000), n_patients))
    with open(os.path.join(out, "SAMPLED_PATIENTS"), "w") as f:
        f.write("\n".join(f"p{p:05d}" for p in pids))
    jobs = []
    for p in pids:
        d = f"p{p // 1000:02d}/p{p:05d}"
        for s in range(n_segments):
            for e in ("atr", "hea"):
                jobs.append((f"{BASE}/{ICENTIA}/{d}/p{p:05d}_s{s:02d}.{e}", os.path.join(out, d, f"p{p:05d}_s{s:02d}.{e}")))
    for x in EXTRA["icentia11k"]:
        jobs.append((f"{BASE}/{ICENTIA}/{x}", os.path.join(out, x)))
    with ThreadPoolExecutor(workers) as ex:
        ok = list(ex.map(lambda j: fetch(*j), jobs))
    print(f"[icentia11k] patients={n_patients} segments/patient={n_segments} files={len(jobs)} missing={ok.count(False)}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/raw")
    ap.add_argument("--dbs", nargs="*", default=list(DBS) + ["icentia11k"])
    ap.add_argument("--icentia-patients", type=int, default=800)
    ap.add_argument("--icentia-segments", type=int, default=10)
    ap.add_argument("--icentia-seed", type=int, default=20261110)
    a = ap.parse_args()
    for db in a.dbs:
        if db == "icentia11k":
            download_icentia(a.root, a.icentia_patients, a.icentia_segments, a.icentia_seed)
        else:
            download_db(db, a.root)
