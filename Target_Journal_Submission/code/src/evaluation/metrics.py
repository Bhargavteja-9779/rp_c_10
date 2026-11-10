"""Window-level and patient-level evaluation metrics."""
from __future__ import annotations
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score

THRESHOLDS = {"present_30s": None, "ge1pct": 0.01, "ge10pct": 0.10}


def window_metrics(y, p, d=None, thr=0.5):
    y = y.astype(int); h = (p >= thr).astype(int)
    tp = ((h == 1) & (y == 1)).sum(); tn = ((h == 0) & (y == 0)).sum()
    fp = ((h == 1) & (y == 0)).sum(); fn = ((h == 0) & (y == 1)).sum()
    out = dict(n_windows=len(y), prevalence=y.mean(), tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn),
               sensitivity=tp / max(tp + fn, 1), specificity=tn / max(tn + fp, 1),
               ppv=tp / max(tp + fp, 1), f1=f1_score(y, h, zero_division=0),
               brier=float(np.mean((p - y) ** 2)), ece=ece(y, p))
    if 0 < y.mean() < 1:
        out["auroc"] = roc_auc_score(y, p); out["auprc"] = average_precision_score(y, p)
    else:
        out["auroc"] = np.nan; out["auprc"] = np.nan
    return out


def ece(y, p, n_bins=15):
    bins = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    e = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            e += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(e)


def lin_ccc(a, b):
    ma, mb = a.mean(), b.mean(); va, vb = a.var(), b.var()
    return float(2 * np.cov(a, b, bias=True)[0, 1] / (va + vb + (ma - mb) ** 2 + 1e-12))


def burden_metrics(B, Bh, hours=None):
    """B, Bh in fraction units; errors reported in percentage points (pp)."""
    e = (Bh - B) * 100
    ae = np.abs(e)
    out = dict(n_patients=len(B), mae_pp=ae.mean(), median_ae_pp=np.median(ae), rmse_pp=np.sqrt((e ** 2).mean()),
               bias_pp=e.mean(), loa_low_pp=e.mean() - 1.96 * e.std(ddof=1) if len(e) > 1 else np.nan,
               loa_high_pp=e.mean() + 1.96 * e.std(ddof=1) if len(e) > 1 else np.nan,
               p90_ae_pp=np.percentile(ae, 90), ccc=lin_ccc(B, Bh) if len(B) > 2 else np.nan)
    free = B == 0
    out["n_af_free"] = int(free.sum())
    out["af_free_mean_false_burden_pp"] = float(ae[free].mean()) if free.any() else np.nan
    out["mae_af_present_pp"] = float(ae[~free].mean()) if (~free).any() else np.nan
    for name, t in THRESHOLDS.items():
        if t is None:
            if hours is None:
                continue
            truth = B * hours * 3600 >= 30; pred = Bh * hours * 3600 >= 30
        else:
            truth = B >= t; pred = Bh >= t
        out[f"{name}_sens"] = float((pred & truth).sum() / max(truth.sum(), 1)) if truth.any() else np.nan
        out[f"{name}_spec"] = float((~pred & ~truth).sum() / max((~truth).sum(), 1)) if (~truth).any() else np.nan
        out[f"{name}_acc"] = float((pred == truth).mean())
    return out


def interval_metrics(B, lo, hi):
    cov = (B >= lo - 1e-12) & (B <= hi + 1e-12)
    return dict(coverage=float(cov.mean()), mean_width_pp=float((hi - lo).mean() * 100),
                median_width_pp=float(np.median(hi - lo) * 100),
                coverage_af_free=float(cov[B == 0].mean()) if (B == 0).any() else np.nan,
                coverage_af_present=float(cov[B > 0].mean()) if (B > 0).any() else np.nan)


def curves(y, p, n_points=300):
    """Down-sampled ROC and PR curve points for figure regeneration."""
    from sklearn.metrics import roc_curve, precision_recall_curve
    if not (0 < y.mean() < 1):
        return None
    fpr, tpr, _ = roc_curve(y, p)
    pr, rc, _ = precision_recall_curve(y, p)
    i = np.unique(np.linspace(0, len(fpr) - 1, n_points).astype(int)); j = np.unique(np.linspace(0, len(pr) - 1, n_points).astype(int))
    return dict(roc_fpr=fpr[i], roc_tpr=tpr[i], pr_recall=rc[j], pr_precision=pr[j])
