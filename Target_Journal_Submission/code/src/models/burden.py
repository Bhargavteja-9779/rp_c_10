"""Patient-level AF-burden estimators built on top of any window-level detector.

Burden is a per-patient *prevalence* (time fraction in AF). Notation: window j of patient i has
duration d_ij, detector probability p_ij, (unknown) label y_ij. All calibration quantities are
estimated on held-out calibration patients (set "calA"); nothing is estimated on test patients
except the unsupervised per-patient quantities of EMQ and PA-HMMQ.

Estimators
  CC        classify-and-count (threshold 0.5), duration-weighted
  CC-MF     CC after a 3-window median filter (common temporal smoothing post-processing)
  PCC       probabilistic classify-and-count (mean probability)
  PCC-iso   PCC with source isotonic recalibration of probabilities
  ACC       adjusted classify-and-count: (CC - FPR) / (TPR - FPR)          (Forman 2008)
  PACC      probabilistic ACC with class-conditional mean probabilities    (Bella et al. 2010)
  EMQ       EM prior adjustment per patient (Saerens et al. 2002)
  HMM-src   2-state HMM, fixed source dynamics and calibrated emissions (no adaptation)
  PA-HMMQ   proposed: patient-adaptive HMM quantification (MAP-EM on dynamics, fixed emissions)
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import median_filter
from sklearn.isotonic import IsotonicRegression
from .hmm import BurdenHMM

ESTIMATORS = ["CC", "CC-MF", "PCC", "PCC-iso", "ACC", "PACC", "EMQ", "HMM-src", "PA-HMMQ"]
P_CLIP = 1e-6


def _logit(p):
    p = np.clip(p, P_CLIP, 1 - P_CLIP)
    return np.log(p) - np.log1p(-p)


def group_mean(values, weights, groups, n):
    num = np.bincount(groups, weights=values * weights, minlength=n)
    den = np.bincount(groups, weights=weights, minlength=n)
    return num / np.maximum(den, 1e-12)


class EmissionModel:
    """Class-conditional densities of logit(p) via Laplace-smoothed histograms."""
    def __init__(self, bins=50, lo=-14.0, hi=14.0, alpha=1.0):
        self.edges = np.linspace(lo, hi, bins + 1); self.alpha = alpha

    def fit(self, p, y):
        z = np.clip(_logit(p), self.edges[0] + 1e-9, self.edges[-1] - 1e-9)
        w = np.diff(self.edges)
        self.dens = []
        for k in (0, 1):
            h, _ = np.histogram(z[y == k], self.edges)
            h = h + self.alpha
            self.dens.append(h / h.sum() / w)
        return self

    def __call__(self, p):
        z = np.clip(_logit(p), self.edges[0] + 1e-9, self.edges[-1] - 1e-9)
        b = np.clip(np.searchsorted(self.edges, z) - 1, 0, len(self.edges) - 2)
        return np.stack([self.dens[0][b], self.dens[1][b]], 1)


class RawEmission:
    """Emission likelihoods taken directly from the detector probability: e(x|AF) ∝ p, e(x|non-AF) ∝ 1-p
    (i.e. the detector's posterior under a balanced training prior is used as a likelihood ratio)."""
    def __call__(self, p):
        p = np.clip(p, P_CLIP, 1 - P_CLIP)
        return np.stack([1 - p, p], 1)


class BurdenCalibrator:
    """Holds every source-calibration quantity, estimated on calibration patients only."""
    def __init__(self, thr=0.5, kappa=10.0, bins=50):
        self.thr, self.kappa, self.bins = thr, kappa, bins

    def fit(self, p, y, d, seq_index):
        h = (p >= self.thr).astype(float)
        w1, w0 = d * (y == 1), d * (y == 0)
        self.tpr = (h * w1).sum() / w1.sum(); self.fpr = (h * w0).sum() / w0.sum()
        self.m1 = (p * w1).sum() / w1.sum(); self.m0 = (p * w0).sum() / w0.sum()
        self.prior = w1.sum() / d.sum()
        self.iso = IsotonicRegression(y_min=P_CLIP, y_max=1 - P_CLIP, out_of_bounds="clip").fit(p, y, sample_weight=d)
        self.emis = EmissionModel(bins=self.bins).fit(p, y)
        self.emis_raw = RawEmission()
        self.hmm_src = BurdenHMM(kappa=None).fit_source(y.astype(int), seq_index)
        self.hmm_pa = BurdenHMM(kappa=self.kappa).fit_source(y.astype(int), seq_index)
        return self


def _seq_index(seqkey):
    """Map string sequence keys to consecutive ints preserving first-appearance order."""
    _, first, inv = np.unique(seqkey, return_index=True, return_inverse=True)
    rank = np.empty(len(first), dtype=np.int64); rank[np.argsort(first)] = np.arange(len(first))
    return rank[inv]


def estimate(cal: BurdenCalibrator, p, d, seqkey, patient, estimators=ESTIMATORS, n_samples=200, seed=0, raw_emission=False):
    """Return dict estimator -> per-patient burden array, the list of patients, and
    posterior burden samples for PA-HMMQ (K, P) when n_samples > 0."""
    pats, pidx = np.unique(patient, return_inverse=True)
    P = len(pats)
    sidx = _seq_index(seqkey)
    out = {}
    h = (p >= cal.thr).astype(float)
    if "CC" in estimators:
        out["CC"] = group_mean(h, d, pidx, P)
    if "CC-MF" in estimators:
        hm = h.copy()
        for s in np.unique(sidx):
            m = sidx == s
            if m.sum() >= 3:
                hm[m] = median_filter(h[m], size=3, mode="nearest")
        out["CC-MF"] = group_mean(hm, d, pidx, P)
    if "PCC" in estimators:
        out["PCC"] = group_mean(p, d, pidx, P)
    pc = cal.iso.predict(p)
    if "PCC-iso" in estimators:
        out["PCC-iso"] = group_mean(pc, d, pidx, P)
    if "ACC" in estimators:
        cc = group_mean(h, d, pidx, P)
        out["ACC"] = np.clip((cc - cal.fpr) / max(cal.tpr - cal.fpr, 1e-6), 0, 1)
    if "PACC" in estimators:
        pcc = group_mean(p, d, pidx, P)
        out["PACC"] = np.clip((pcc - cal.m0) / max(cal.m1 - cal.m0, 1e-6), 0, 1)
    if "EMQ" in estimators:
        pi = cal.prior
        b = np.full(P, pi)
        pcl = np.clip(pc, P_CLIP, 1 - P_CLIP)
        for _ in range(200):
            bi = b[pidx]
            num = (bi / pi) * pcl; den = num + ((1 - bi) / (1 - pi)) * (1 - pcl)
            nb = group_mean(num / den, d, pidx, P)
            if np.max(np.abs(nb - b)) < 1e-7:
                b = nb; break
            b = nb
        out["EMQ"] = b
    samples = None
    if "HMM-src" in estimators or "PA-HMMQ" in estimators:
        E = cal.emis_raw(p) if raw_emission else cal.emis(p)
        # patient of each sequence
        pos = np.zeros(sidx.max() + 1, dtype=np.int64); pos[sidx] = pidx
        if "HMM-src" in estimators:
            g, _ = cal.hmm_src.infer(E, sidx, pos, P)
            out["HMM-src"] = group_mean(g, d, pidx, P)
        if "PA-HMMQ" in estimators:
            g, S = cal.hmm_pa.infer(E, sidx, pos, P, n_samples=n_samples, rng=np.random.default_rng(seed))
            out["PA-HMMQ"] = group_mean(g, d, pidx, P)
            if S is not None:
                den = np.bincount(pidx, weights=d, minlength=P)
                samples = np.stack([np.bincount(pidx, weights=S[k] * d, minlength=P) / den for k in range(S.shape[0])])
    return out, pats, samples


def true_burden(af_frac, d, patient):
    pats, pidx = np.unique(patient, return_inverse=True)
    return group_mean(af_frac, d, pidx, len(pats)), pats
