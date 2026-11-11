"""Statistical procedures (pre-specified; see supplementary S1)."""
from __future__ import annotations
import numpy as np
from scipy import stats


def paired_wilcoxon(a: np.ndarray, b: np.ndarray, n_boot: int = 2000, seed: int = 0):
    """Two-sided Wilcoxon signed-rank test on paired per-patient values a vs b (unit = patient).
    Returns p-value, number of non-zero pairs, median and mean paired difference (a-b) with
    patient-level bootstrap 95% CIs, and the matched-pairs rank-biserial correlation."""
    d = a - b
    nz = d[d != 0]
    if len(nz) < 1:
        p = 1.0
    else:
        p = float(stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided").pvalue)
    ranks = stats.rankdata(np.abs(nz)) if len(nz) else np.array([])
    wpos, wneg = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    rbc = float((wpos - wneg) / (wpos + wneg)) if len(nz) else 0.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), (n_boot, len(d)))
    bmed = np.median(d[idx], axis=1); bmean = d[idx].mean(1)
    return dict(n=len(d), n_nonzero=int(len(nz)), p=p,
                median_diff=float(np.median(d)), median_ci=(float(np.percentile(bmed, 2.5)), float(np.percentile(bmed, 97.5))),
                mean_diff=float(d.mean()), mean_ci=(float(np.percentile(bmean, 2.5)), float(np.percentile(bmean, 97.5))),
                rank_biserial=rbc)


def holm(pvals: dict) -> dict:
    keys = sorted(pvals, key=lambda k: pvals[k])
    m = len(keys); out = {}; running = 0.0
    for i, k in enumerate(keys):
        adj = min(1.0, (m - i) * pvals[k]); running = max(running, adj); out[k] = running
    return out


def mcnemar(pred_a: np.ndarray, pred_b: np.ndarray, truth: np.ndarray):
    """Exact McNemar test on paired correctness of two binary classifications."""
    ca, cb = pred_a == truth, pred_b == truth
    n01 = int((ca & ~cb).sum()); n10 = int((~ca & cb).sum())
    n = n01 + n10
    p = 1.0 if n == 0 else float(stats.binomtest(min(n01, n10), n, 0.5).pvalue)
    return dict(a_correct_b_wrong=n01, a_wrong_b_correct=n10, p=p)


def clopper_pearson(k: int, n: int, level: float = 0.95):
    a = 1 - level
    lo = stats.beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = stats.beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return float(lo), float(hi)


def bootstrap_mean_ci(x: np.ndarray, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    b = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
