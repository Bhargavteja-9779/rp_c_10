import os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.training.splits import patient_split
from src.preprocessing.windows import make_windows
from src.preprocessing.features import rr_features, FEATURE_NAMES
from src.preprocessing.perturb import perturb_record
from src.models.hmm import BurdenHMM
from src.models.burden import BurdenCalibrator, estimate, true_burden
from src.models.conformal import conformal_quantile, fit_interval, predict_interval
from src.statistics.tests import holm, paired_wilcoxon, clopper_pearson


def _rec(n=600, af_from=200, af_to=400, seed=0):
    rng = np.random.default_rng(seed)
    rr = np.full(n, 0.8, np.float32); rh = np.zeros(n, np.int8)
    rr[af_from:af_to] = rng.uniform(0.4, 1.0, af_to - af_from); rh[af_from:af_to] = 1
    return dict(rr=rr, rhythm=rh, beat=np.zeros(n, np.int8), seq=np.zeros(n, np.int32), valid=np.ones(n, bool),
                patient="p", record="r", db="t")


def test_splits_disjoint_and_complete():
    pats = np.array([f"p{i}" for i in range(100)]); dbs = np.array(["a"] * 50 + ["b"] * 50); af = np.arange(100) % 2 == 0
    sp = patient_split(pats, dbs, af, {"train": .45, "calA": .15, "calB": .2, "test": .2}, 1)
    allp = set().union(*sp.values())
    assert allp == set(pats)
    for a in sp:
        for b in sp:
            if a < b: assert not (sp[a] & sp[b])


def test_windows_labels_and_time():
    w = make_windows(_rec(), 60)
    assert w["rr"].shape == (10, 60)
    assert np.allclose(w["dur"], w["rr"].sum(1), atol=1e-4)
    assert w["y"].tolist() == [0, 0, 0, 1, 1, 1, 0, 0, 0, 0] or w["y"].sum() in (3, 4)
    tb, _ = true_burden(w["af_frac"], w["dur"], np.array(["p"] * len(w["y"])))
    assert 0 < tb[0] < 1


def test_features_finite():
    x = np.random.default_rng(0).uniform(0.3, 1.5, (50, 60)).astype(np.float32)
    F = rr_features(x)
    assert F.shape == (50, len(FEATURE_NAMES)) and np.isfinite(F).all()


@pytest.mark.parametrize("kind,level", [("missed", .05), ("false", .05), ("jitter", .02), ("ectopy", .1)])
def test_perturbation_preserves_total_time(kind, level):
    r = _rec(); p = perturb_record(r, kind, level, np.random.default_rng(0))
    assert abs(p["rr"].sum() - r["rr"].sum()) < 0.1


def test_hmm_recovers_burden_on_synthetic():
    rng = np.random.default_rng(0)
    y = np.r_[np.zeros(500), np.ones(300), np.zeros(200)].astype(int); seq = np.zeros(1000, int)
    s = np.where(y == 1, rng.normal(1.5, 1, 1000), rng.normal(-1.5, 1, 1000))
    from scipy.stats import norm
    E = np.stack([norm.pdf(s, -1.5, 1), norm.pdf(s, 1.5, 1)], 1)
    h = BurdenHMM(kappa=10).fit_source(y, seq)
    g, S = h.infer(E, seq, np.array([0]), 1, n_samples=20, rng=rng)
    assert abs(g.mean() - 0.3) < 0.03
    assert S.shape == (20, 1000)


def test_acc_unbiased_under_prior_shift():
    rng = np.random.default_rng(1)
    # calibration: detector with TPR .9, FPR .1 ; test patient with burden .2
    n = 20000; y = (rng.random(n) < .5).astype(int)
    p = np.where(y == 1, np.where(rng.random(n) < .9, .9, .1), np.where(rng.random(n) < .1, .9, .1))
    cal = BurdenCalibrator().fit(p, y, np.ones(n), np.arange(n) // 100)
    yt = (rng.random(n) < .2).astype(int)
    pt = np.where(yt == 1, np.where(rng.random(n) < .9, .9, .1), np.where(rng.random(n) < .1, .9, .1))
    e, _, _ = estimate(cal, pt, np.ones(n), np.array([f"s{i//100}" for i in range(n)]), np.array(["p"] * n), ["CC", "ACC"], n_samples=0)
    assert abs(e["ACC"][0] - .2) < .02 and abs(e["CC"][0] - .2) > .05


def test_conformal_coverage_exchangeable():
    rng = np.random.default_rng(2); cov = []
    for _ in range(300):
        r = np.abs(rng.normal(size=51)); q = conformal_quantile(r[:50], .1); cov.append(r[50] <= q)
    assert np.mean(cov) >= .85
    lo, hi = predict_interval(np.array([0.0, 0.5]), 0.1)
    assert lo[0] == 0 and hi[1] == pytest.approx(0.6)


def test_stats_helpers():
    adj = holm({"a": .01, "b": .04, "c": .03})
    assert adj["a"] == pytest.approx(.03) and adj["b"] >= adj["c"]
    r = paired_wilcoxon(np.arange(30.) + 1, np.arange(30.), n_boot=100)
    assert r["p"] < .001 and r["rank_biserial"] == 1
    lo, hi = clopper_pearson(90, 100); assert lo < .9 < hi
