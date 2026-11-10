"""Parse PhysioNet annotation files into per-recording RR-interval series.

Output per recording (dict):
  db, record, patient, rr (float32 seconds), rhythm (int8: 0=non-AF, 1=AF, 2=AFL, -1=unlabeled),
  beat (int8: 0=normal, 1=supraventricular ectopic, 2=ventricular ectopic, 3=unclassifiable/other),
  seq (int32 sequence id: RR intervals are only contiguous within a sequence; Icentia segments
  are separate sequences), valid (bool: physiologically plausible RR and labelled rhythm).
RR_k = t_k - t_{k-1} takes the rhythm label active at beat t_k and the beat type of beat t_k.
"""
from __future__ import annotations
import csv, glob, os, re
import numpy as np
import wfdb

BEAT_SYMBOLS = set("NLRBAaJSVrFejnE/fQ?")
SVE = set("AaJSje")          # supraventricular ectopic / escape (AAMI S-like)
VE = set("VrEF!")             # ventricular ectopic (AAMI V/F-like)
UNK = set("Q?/f")             # unclassifiable / paced
RR_MIN, RR_MAX = 0.2, 3.0     # plausibility limits (s)


def rhythm_code(aux: str) -> int | None:
    a = aux.strip().replace("\x00", "")
    if not a.startswith("("):
        return None
    a = a[1:].upper()
    if a in ("AFIB", "AF", "AFF"):
        return 1
    if a in ("AFL",):
        return 2
    return 0


def _beat_code(sym: str) -> int:
    if sym in SVE: return 1
    if sym in VE: return 2
    if sym in UNK: return 3
    return 0


def _rhythm_at(beat_samples, change_samples, change_codes, default):
    """Rhythm active at each beat sample, given rhythm-change annotations (sorted)."""
    out = np.full(len(beat_samples), default, dtype=np.int8)
    if len(change_samples) == 0:
        return out
    idx = np.searchsorted(change_samples, beat_samples, side="right") - 1
    has = idx >= 0
    out[has] = np.asarray(change_codes, dtype=np.int8)[idx[has]]
    return out


def _build(samples, symbols, rhythm, fs, seq_id=0):
    samples = np.asarray(samples, dtype=np.int64)
    keep = np.array([s in BEAT_SYMBOLS for s in symbols], dtype=bool)
    bs = samples[keep]; bsym = [s for s, k in zip(symbols, keep) if k]; brh = rhythm[keep]
    order = np.argsort(bs, kind="stable"); bs = bs[order]; brh = brh[order]; bsym = [bsym[i] for i in order]
    rr = np.diff(bs) / float(fs)
    rh = brh[1:].astype(np.int8)
    bt = np.array([_beat_code(s) for s in bsym[1:]], dtype=np.int8)
    valid = (rr >= RR_MIN) & (rr <= RR_MAX) & (rh >= 0)
    return dict(rr=rr.astype(np.float32), rhythm=rh, beat=bt, valid=valid,
                seq=np.full(len(rr), seq_id, dtype=np.int32))


def _concat(parts):
    if not parts:
        return None
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


def parse_standard(path_noext: str, beat_ext: str, rhythm_ext: str | None = None, default_rhythm: int = 0):
    """Beats and rhythm changes in one file (beat_ext) or rhythm in a second file (rhythm_ext)."""
    a = wfdb.rdann(path_noext, beat_ext)
    fs = a.fs or wfdb.rdheader(path_noext).fs
    if rhythm_ext is None:
        rsrc = a
    else:
        rsrc = wfdb.rdann(path_noext, rhythm_ext)
    ch_s, ch_c = [], []
    for s, x in zip(rsrc.sample, rsrc.aux_note):
        c = rhythm_code(x or "")
        if c is not None:
            ch_s.append(int(s)); ch_c.append(c)
    order = np.argsort(ch_s, kind="stable")
    ch_s = np.asarray(ch_s, dtype=np.int64)[order]; ch_c = np.asarray(ch_c, dtype=np.int8)[order] if len(ch_c) else np.array([], np.int8)
    rh = _rhythm_at(np.asarray(a.sample), ch_s, ch_c, default_rhythm)
    return _build(a.sample, a.symbol, rh, fs)


def parse_icentia_segment(path_noext: str, seq_id: int):
    """Icentia11k: rhythm regions '(X' ... ')' ; beats outside regions are unlabeled (-1)."""
    a = wfdb.rdann(path_noext, "atr")
    fs = a.fs or 250
    smp = np.asarray(a.sample, dtype=np.int64)
    rh = np.full(len(smp), -1, dtype=np.int8)
    cur = -1
    # annotations are time-ordered; walk once
    for i, (s, x) in enumerate(zip(smp, a.aux_note)):
        x = (x or "").strip()
        if x.startswith("("):
            cur = rhythm_code(x)
        elif x == ")":
            rh[i] = cur  # the closing marker itself is not a beat
            cur = -1
            continue
        rh[i] = cur
    return _build(smp, a.symbol, rh, fs, seq_id)


def _shdb_patient_map(root):
    p = os.path.join(root, "shdb-af", "AdditionalData.csv")
    m = {}
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                uid = (row.get("UID") or "").strip()
                if uid:
                    m[uid.zfill(3)] = "shdb_" + (row.get("Study ID") or uid).strip()
    return m


def load_database(name: str, root: str):
    """Return a list of recording dicts for database `name`."""
    d = os.path.join(root, name)
    recs = []
    if name == "icentia11k":
        pids = [l.strip() for l in open(os.path.join(d, "SAMPLED_PATIENTS")) if l.strip()]
        for pid in pids:
            segs = sorted(glob.glob(os.path.join(d, pid[:3], pid, f"{pid}_s*.atr")))
            parts = [parse_icentia_segment(s[:-4], k) for k, s in enumerate(segs)]
            r = _concat(parts)
            if r is not None:
                recs.append(dict(db=name, record=pid, patient=f"icentia_{pid}", **r))
        return recs
    records = [l.strip() for l in open(os.path.join(d, "RECORDS")) if l.strip()]
    shdb = _shdb_patient_map(root) if name == "shdb-af" else {}
    for r in records:
        base = os.path.join(d, r)
        try:
            if name in ("ltafdb", "mitdb", "cpsc2021"):
                out = parse_standard(base, "atr")
            elif name == "nsrdb":
                out = parse_standard(base, "atr")
            elif name in ("nsr2db", "chfdb"):
                out = parse_standard(base, "ecg")
            elif name in ("afdb", "shdb-af"):
                if not (os.path.exists(base + ".qrs") and os.path.exists(base + ".atr")):
                    continue  # unannotated recording (SHDB-AF) or missing beats
                out = parse_standard(base, "qrs", rhythm_ext="atr")
            else:
                raise ValueError(name)
        except FileNotFoundError:
            continue
        if name == "mitdb":
            patient = "mitdb_201" if r in ("201", "202") else f"mitdb_{r}"  # 201/202 same subject
        elif name == "cpsc2021":
            m = re.match(r"(Training_set_I+)/data_(\d+)_(\d+)", r)
            patient = f"cpsc_{m.group(1)[-2:]}_{m.group(2)}"
        elif name == "shdb-af":
            patient = shdb.get(r.zfill(3), f"shdb_uid{r}")
        else:
            patient = f"{name}_{r}"
        recs.append(dict(db=name, record=r, patient=patient, **out))
    return recs
