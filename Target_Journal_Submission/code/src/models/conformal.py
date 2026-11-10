"""Split-conformal prediction intervals for per-patient AF burden.

Nonconformity (normalised): r_i = |B_i - B_hat_i| / (sigma_i + eps), where sigma_i is the
posterior standard deviation of patient i's burden under PA-HMMQ (FFBS samples).
Constant-width variant: r_i = |B_i - B_hat_i|. With n calibration patients the threshold is the
ceil((n+1)(1-alpha))-th smallest score (finite-sample marginal coverage >= 1-alpha under
exchangeability of patients; Vovk et al. 2005; Lei et al. 2018). Intervals are clipped to [0,1].
"""
from __future__ import annotations
import numpy as np


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if k > n:
        return np.inf
    return float(np.sort(scores)[k - 1])


def fit_interval(B_true, B_hat, sigma=None, alpha=0.1, eps=0.002):
    if sigma is None:
        return conformal_quantile(np.abs(B_true - B_hat), alpha)
    return conformal_quantile(np.abs(B_true - B_hat) / (sigma + eps), alpha)


def predict_interval(B_hat, q, sigma=None, eps=0.002):
    half = q if sigma is None else q * (sigma + eps)
    return np.clip(B_hat - half, 0, 1), np.clip(B_hat + half, 0, 1)
