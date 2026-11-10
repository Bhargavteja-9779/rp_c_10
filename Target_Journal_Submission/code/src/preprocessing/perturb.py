"""Simulated RR-series perturbations for robustness testing (applied to beat time series)."""
from __future__ import annotations
import numpy as np
from ..data.records import RR_MIN, RR_MAX


def perturb_record(rec: dict, kind: str, level: float, rng: np.random.Generator) -> dict:
    """kind: 'missed' (delete beats with prob level), 'false' (insert spurious beats with prob level),
    'jitter' (Gaussian R-peak timing noise, SD=level seconds), 'ectopy' (premature beat with
    compensatory pause with prob level: RR_k *= 0.65, RR_{k+1} += 0.35*RR_k_original)."""
    rr = rec["rr"].astype(np.float64).copy(); rh = rec["rhythm"].copy(); bt = rec["beat"].copy(); seq = rec["seq"].copy()
    if kind == "none":
        pass
    elif kind == "missed":
        drop = rng.random(len(rr)) < level
        drop[-1] = False
        keep_rr, keep_rh, keep_bt, keep_seq = [], [], [], []
        acc = 0.0
        for i in range(len(rr)):
            acc += rr[i]
            if drop[i] and seq[i] == seq[min(i + 1, len(rr) - 1)]:
                continue  # beat i missed: its interval merges with the next one
            keep_rr.append(acc); keep_rh.append(rh[i]); keep_bt.append(bt[i]); keep_seq.append(seq[i]); acc = 0.0
        rr, rh, bt, seq = map(np.asarray, (keep_rr, keep_rh, keep_bt, keep_seq))
    elif kind == "false":
        ins = rng.random(len(rr)) < level
        frac = rng.uniform(0.3, 0.7, len(rr))
        n_rr = np.empty(len(rr) + ins.sum()); n_rh = np.empty(len(n_rr), np.int8); n_bt = np.empty(len(n_rr), np.int8); n_seq = np.empty(len(n_rr), np.int32)
        j = 0
        for i in range(len(rr)):
            if ins[i]:
                n_rr[j] = rr[i] * frac[i]; n_rh[j] = rh[i]; n_bt[j] = 3; n_seq[j] = seq[i]; j += 1
                n_rr[j] = rr[i] * (1 - frac[i])
            else:
                n_rr[j] = rr[i]
            n_rh[j] = rh[i]; n_bt[j] = bt[i]; n_seq[j] = seq[i]; j += 1
        rr, rh, bt, seq = n_rr, n_rh, n_bt, n_seq
    elif kind == "jitter":
        t = np.cumsum(rr)
        t = t + rng.normal(0, level, len(t))
        rr = np.diff(np.r_[0.0, t])
    elif kind == "ectopy":
        ect = rng.random(len(rr)) < level
        ect[-1] = False
        for i in np.flatnonzero(ect):
            if seq[i] != seq[i + 1]:
                continue
            short = 0.35 * rr[i]
            rr[i] -= short; rr[i + 1] += short; bt[i] = 1
    else:
        raise ValueError(kind)
    valid = (rr >= RR_MIN) & (rr <= RR_MAX) & (rh >= 0)
    return dict(rec, rr=rr.astype(np.float32), rhythm=rh.astype(np.int8), beat=bt.astype(np.int8),
                seq=seq.astype(np.int32), valid=valid)
