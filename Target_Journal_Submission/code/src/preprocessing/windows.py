"""Segment RR series into non-overlapping fixed-length beat windows (per recording)."""
from __future__ import annotations
import numpy as np


def make_windows(rec: dict, W: int = 60):
    """Cut non-overlapping windows of W consecutive *valid* RR intervals that do not cross
    sequence boundaries or invalid intervals. Returns dict of arrays (one row per window),
    windows ordered in time. Reference labels are derived from per-beat rhythm annotations."""
    rr, rh, bt, valid, seq = rec["rr"], rec["rhythm"], rec["beat"], rec["valid"], rec["seq"]
    n = len(rr)
    # runs of consecutive valid intervals within the same sequence
    brk = np.ones(n, dtype=bool)
    brk[1:] = (seq[1:] != seq[:-1]) | (~valid[:-1])
    starts = np.flatnonzero(brk & valid)
    idx = []
    run_id = []
    for k, s in enumerate(starts):
        e = s
        while e < n and valid[e] and seq[e] == seq[s]:
            e += 1
        m = (e - s) // W
        for j in range(m):
            idx.append(s + j * W)
            run_id.append(int(seq[s]))
    if not idx:
        return None
    idx = np.asarray(idx)
    take = idx[:, None] + np.arange(W)[None, :]
    R = rr[take]
    H = rh[take]
    B = bt[take]
    dur = R.sum(1)
    af_frac = (R * (H == 1)).sum(1) / dur          # time-weighted AF fraction in window
    afl_frac = (R * (H == 2)).sum(1) / dur
    return dict(
        rr=R.astype(np.float32), dur=dur.astype(np.float32),
        af_frac=af_frac.astype(np.float32), afl_frac=afl_frac.astype(np.float32),
        y=(af_frac >= 0.5).astype(np.int8),
        ect_sv=(B == 1).mean(1).astype(np.float32), ect_v=(B == 2).mean(1).astype(np.float32),
        unk=(B == 3).mean(1).astype(np.float32),
        seq=np.asarray(run_id, dtype=np.int32), start_beat=idx.astype(np.int64),
    )
