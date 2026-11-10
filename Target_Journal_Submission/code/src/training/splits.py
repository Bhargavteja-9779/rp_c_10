"""Patient-level, stratified (database x AF-presence) splits. No patient appears in two splits."""
from __future__ import annotations
import numpy as np


def patient_split(patients, dbs, has_af, fracs: dict, seed: int):
    """Return dict split_name -> set(patients). fracs keys in order, summing to 1."""
    rng = np.random.default_rng(seed)
    names = list(fracs)
    out = {k: set() for k in names}
    strata = {}
    for p, d, a in zip(patients, dbs, has_af):
        strata.setdefault((d, bool(a)), []).append(p)
    for key in sorted(strata):
        ps = sorted(strata[key]); rng.shuffle(ps)
        n = len(ps)
        cuts = np.round(np.cumsum([fracs[k] for k in names]) * n).astype(int)
        start = 0
        for k, c in zip(names, cuts):
            out[k].update(ps[start:c]); start = c
    return out
