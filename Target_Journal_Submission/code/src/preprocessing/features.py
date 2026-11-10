"""Vectorised RR-interval features (classical AF detection features from the literature).

Features (per window of W RR intervals, seconds):
  mean RR, SDNN, CV, RMSSD (normalised by mean RR), pNN50, pNN20, median |dRR| / mean RR,
  IQR/median RR, turning-point ratio, Shannon entropy of the RR histogram (Dash et al. 2009),
  Poincare SD1/SD2 and SD1/SD2 ratio, coefficient of sample entropy (COSEn, Lake & Moorman 2011),
  fraction of successive-difference sign changes, min/max RR ratio.
"""
from __future__ import annotations
import numpy as np

FEATURE_NAMES = ["mean_rr", "sdnn", "cv", "nrmssd", "pnn50", "pnn20", "nmad_drr", "iqr_med",
                 "tpr", "shannon", "sd1", "sd2", "sd1_sd2", "cosen", "sign_change", "minmax"]


def _sampen(x, m=2, r_frac=0.2):
    """Sample entropy for each row of x (B, n) with tolerance r = r_frac * SD (vectorised)."""
    B, n = x.shape
    r = r_frac * x.std(1, keepdims=True) + 1e-9
    def count(mm):
        emb = np.stack([x[:, i:n - mm + i + 1] for i in range(mm)], axis=2)  # (B, n-mm+1, mm)
        d = np.abs(emb[:, :, None, :] - emb[:, None, :, :]).max(-1)          # Chebyshev
        k = emb.shape[1]
        mask = ~np.eye(k, dtype=bool)
        return ((d <= r[:, :, None]) & mask[None]).sum((1, 2)).astype(np.float64)
    # use the same number of templates (n-m) for both lengths
    A = count(m + 1)
    Bm = count(m)
    with np.errstate(divide="ignore", invalid="ignore"):
        se = -np.log((A + 1e-3) / (Bm + 1e-3))
    return se


def rr_features(R: np.ndarray, batch: int = 4000) -> np.ndarray:
    R = R.astype(np.float64)
    out = []
    for s in range(0, len(R), batch):
        x = R[s:s + batch]
        mu = x.mean(1); sd = x.std(1)
        d = np.diff(x, axis=1); ad = np.abs(d)
        rmssd = np.sqrt((d ** 2).mean(1))
        pnn50 = (ad > 0.05).mean(1); pnn20 = (ad > 0.02).mean(1)
        nmad = np.median(ad, 1) / mu
        q75, q25 = np.percentile(x, [75, 25], axis=1)
        iqr_med = (q75 - q25) / np.median(x, 1)
        tp = ((x[:, 1:-1] > x[:, :-2]) & (x[:, 1:-1] > x[:, 2:])) | ((x[:, 1:-1] < x[:, :-2]) & (x[:, 1:-1] < x[:, 2:]))
        tpr = tp.mean(1)
        # Shannon entropy of RR histogram (16 bins between min and max of each window)
        lo = x.min(1, keepdims=True); hi = x.max(1, keepdims=True)
        bins = np.clip(((x - lo) / (hi - lo + 1e-9) * 16).astype(int), 0, 15)
        H = np.zeros((len(x), 16)); np.add.at(H, (np.repeat(np.arange(len(x)), x.shape[1]), bins.ravel()), 1)
        P = H / x.shape[1]
        with np.errstate(divide="ignore", invalid="ignore"):
            shannon = -(np.where(P > 0, P * np.log(P), 0)).sum(1) / np.log(16)
        sd1 = np.sqrt(0.5) * d.std(1)
        sd2 = np.sqrt(np.maximum(2 * sd ** 2 - 0.5 * d.std(1) ** 2, 1e-12))
        se = _sampen(x)
        cosen = se + np.log(2 * 0.03) - np.log(mu)      # COSEn with r fixed relative term (approximation)
        sc = (np.sign(d[:, 1:]) != np.sign(d[:, :-1])).mean(1)
        mm = x.min(1) / x.max(1)
        out.append(np.stack([mu, sd, sd / mu, rmssd / mu, pnn50, pnn20, nmad, iqr_med, tpr, shannon,
                             sd1 / mu, sd2 / mu, sd1 / (sd2 + 1e-9), cosen, sc, mm], 1))
    F = np.concatenate(out).astype(np.float32)
    return np.nan_to_num(F, nan=0.0, posinf=10.0, neginf=-10.0)
