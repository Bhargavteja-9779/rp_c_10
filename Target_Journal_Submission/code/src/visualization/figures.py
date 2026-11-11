"""All manuscript figures, generated from machine-readable result files only."""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.visualization import style
from src.visualization.style import plt, SERIES, TEXT, TEXT2, COHORT_ORDER, COHORT_LABEL, COHORT_COLOR, DET_COLOR, save
from matplotlib.patches import FancyBboxPatch

EXT = ["ext_shdb-af", "ext_cpsc2021", "ext_icentia11k"]
EST_ORDER = ["CC", "CC-MF", "PCC", "PCC-iso", "ACC", "PACC", "EMQ", "HMM-src", "PA-HMMQ", "PA-HMMQ[rawE]"]
EST_LABEL = {"PA-HMMQ": "PA-HMMQ (pre-reg., calibrated emissions)", "PA-HMMQ[rawE]": "PA-HMMQ (final, probability emissions)"}


def fig_method(out):
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    boxes = [(0.1, 2.2, 1.7, 1.3, "Ambulatory ECG\nbeat annotations\n→ RR intervals"),
             (2.1, 2.2, 1.7, 1.3, "60-beat windows\n(non-overlapping)"),
             (4.1, 2.2, 1.9, 1.3, "Window detector\n(Classical-LR /\nLightGBM / RRNet)\n→ p(AF | window)"),
             (6.3, 2.2, 1.7, 1.3, "Patient-adaptive\nHMM quantifier\n(MAP-EM dynamics)"),
             (8.3, 2.2, 1.6, 1.3, "Burden B̂ + 90%\nconformal interval"),
             (4.1, 0.2, 1.9, 1.3, "Calibration patients A\nemissions, source\nrhythm dynamics"),
             (6.3, 0.2, 1.7, 1.3, "Posterior sampling\n(FFBS) → σ̂ per\npatient"),
             (8.3, 0.2, 1.6, 1.3, "Calibration patients B\nconformal quantile")]
    for i, (x, y, w, h, t) in enumerate(boxes):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#f3f2ee" if i < 5 else "#ffffff",
                                    ec=SERIES[0] if i == 3 else TEXT2, lw=1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=7, color=TEXT)
    arr = dict(arrowstyle="->", color=TEXT2, lw=1)
    for x0, x1 in [(1.8, 2.1), (3.8, 4.1), (6.0, 6.3), (8.0, 8.3)]:
        ax.annotate("", (x1, 2.85), (x0, 2.85), arrowprops=arr)
    ax.annotate("", (6.6, 2.2), (5.6, 1.5), arrowprops=arr)
    ax.annotate("", (7.15, 2.2), (7.15, 1.5), arrowprops=arr)
    ax.annotate("", (9.1, 2.2), (9.1, 1.5), arrowprops=arr)
    save(fig, os.path.join(out, "fig1_method"))


def fig_cohorts(R, out):
    one = R[(R.seed == R.seed.min()) & (R.detector == "LightGBM") & (R.estimator == "CC") & R.cohort.isin(COHORT_ORDER)]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for i, c in enumerate(COHORT_ORDER):
        x = one[one.cohort == c]
        b = np.sort(x.true_burden.values * 100)
        axs[0].plot(b, np.arange(1, len(b) + 1) / len(b), color=COHORT_COLOR[c], label=f"{COHORT_LABEL[c]} (n={len(b)})", lw=1.6, drawstyle="steps-post")
        h = np.sort(x.hours.values)
        axs[1].plot(h, np.arange(1, len(h) + 1) / len(h), color=COHORT_COLOR[c], lw=1.6, drawstyle="steps-post")
    axs[0].set_xlabel("Reference AF burden (%)"); axs[0].set_ylabel("Cumulative fraction of patients"); axs[0].legend(loc="lower right")
    axs[1].set_xlabel("Analysed monitoring time per patient (h)"); axs[1].set_xscale("log")
    axs[0].set_title("A  Burden distribution", loc="left"); axs[1].set_title("B  Monitoring duration", loc="left")
    save(fig, os.path.join(out, "fig2_cohorts"))


def fig_training(res, out):
    H = pd.read_csv(os.path.join(res, "training_history.csv"))
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    for s, g in H.groupby("seed"):
        ax.plot(g.epoch, g.train_loss, color=SERIES[0], lw=1, alpha=0.8, label="train" if s == H.seed.min() else None)
        ax.plot(g.epoch, g.val_loss, color=SERIES[1], lw=1, alpha=0.8, label="inner validation" if s == H.seed.min() else None)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Binary cross-entropy"); ax.legend(); ax.set_title("RRNet learning curves (5 seeds)", loc="left")
    save(fig, os.path.join(out, "figS1_training_curves"))


def fig_roc_pr(res, out):
    C = pd.read_csv(os.path.join(res, "curves.csv")); C = C[C.seed == C.seed.min()]
    fig, axs = plt.subplots(2, 4, figsize=(7.2, 3.8), sharey="row")
    for j, c in enumerate(COHORT_ORDER):
        for det, col in DET_COLOR.items():
            for i, cv in enumerate(["roc", "pr"]):
                g = C[(C.cohort == c) & (C.detector == det) & (C.curve == cv)]
                axs[i, j].plot(g.x, g.y, color=col, lw=1.4, label=det)
        axs[0, j].set_title(COHORT_LABEL[c], fontsize=7)
        axs[0, j].set_xlabel("1 − specificity"); axs[1, j].set_xlabel("Recall")
    axs[0, 0].set_ylabel("Sensitivity"); axs[1, 0].set_ylabel("Precision"); axs[0, 0].legend(loc="lower right")
    for a in axs.ravel(): a.set_xlim(0, 1)
    for a in axs[0]: a.set_xlim(0, 0.3)
    fig.tight_layout(); save(fig, os.path.join(out, "figS2_roc_pr"))


def fig_confusion(res, out):
    Wm = pd.read_csv(os.path.join(res, "window_metrics.csv")); Wm = Wm[Wm.detector == "LightGBM"]
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 1.9))
    for j, c in enumerate(COHORT_ORDER):
        g = Wm[Wm.cohort == c][["tn", "fp", "fn", "tp"]].sum()
        m = np.array([[g.tn, g.fp], [g.fn, g.tp]], float); mn = m / m.sum(1, keepdims=True)
        axs[j].imshow(mn, cmap="Blues", vmin=0, vmax=1)
        for (a, b), v in np.ndenumerate(mn):
            axs[j].text(b, a, f"{v:.3f}", ha="center", va="center", color="white" if v > 0.6 else TEXT, fontsize=7)
        axs[j].set_xticks([0, 1], ["non-AF", "AF"]); axs[j].set_yticks([0, 1], ["non-AF", "AF"]); axs[j].grid(False)
        axs[j].set_title(COHORT_LABEL[c], fontsize=7); axs[j].set_xlabel("Predicted")
    axs[0].set_ylabel("Reference")
    save(fig, os.path.join(out, "figS3_confusion_lightgbm"))


def fig_main(per_seed, out, det="LightGBM"):
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 3.0), sharey=True)
    ests = EST_ORDER
    for j, c in enumerate(COHORT_ORDER):
        for i, e in enumerate(ests):
            g = per_seed[(per_seed.detector == det) & (per_seed.estimator == e) & (per_seed.cohort == c)].mae_pp
            col = SERIES[0] if e.startswith("PA-HMMQ") else TEXT2
            axs[j].errorbar(g.mean(), i, xerr=g.std(), fmt="o", ms=4, color=col, ecolor=col, elinewidth=1, capsize=2)
        axs[j].set_title(COHORT_LABEL[c], fontsize=7); axs[j].set_xlabel("MAE (percentage points)")
        axs[j].set_xlim(left=0)
    axs[0].set_yticks(range(len(ests)), [EST_LABEL.get(e, e).replace(" (", "\n(") for e in ests]); axs[0].invert_yaxis()
    fig.suptitle(f"Per-patient AF-burden error by estimator ({det} detector; mean ± SD over 5 seeds)", fontsize=8, x=0.01, ha="left")
    fig.tight_layout(); save(fig, os.path.join(out, "fig3_main_mae"))


def fig_bland_altman(R, out, final, det="LightGBM"):
    x = R[(R.detector == det) & R.cohort.isin(EXT)]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    for ax, est in zip(axs, ["CC", final]):
        g = x[x.estimator == est].groupby(["patient", "cohort"]).agg(t=("true_burden", "first"), e=("estimate", "mean")).reset_index()
        m = (g.t + g.e) / 2 * 100; d = (g.e - g.t) * 100
        for c in EXT:
            k = g.cohort == c
            ax.scatter(m[k], d[k], s=8, color=COHORT_COLOR[c], alpha=0.6, lw=0, label=COHORT_LABEL[c])
        mu, sd = d.mean(), d.std(ddof=1)
        for v, ls in [(mu, "-"), (mu - 1.96 * sd, "--"), (mu + 1.96 * sd, "--")]:
            ax.axhline(v, color=TEXT2, lw=1, ls=ls)
        ax.text(101, mu + 1.96 * sd, f"+1.96 SD {mu+1.96*sd:.1f}", fontsize=6, color=TEXT2, va="bottom", ha="right")
        ax.text(101, mu - 1.96 * sd, f"−1.96 SD {mu-1.96*sd:.1f}", fontsize=6, color=TEXT2, va="top", ha="right")
        ax.set_title(f"{EST_LABEL.get(est, est)}  (bias {mu:.2f} pp)", loc="left", fontsize=7)
        ax.set_xlabel("Mean of estimated and reference burden (%)")
    axs[0].set_ylabel("Estimated − reference (pp)"); axs[0].legend(loc="lower left", fontsize=6)
    save(fig, os.path.join(out, "fig4_bland_altman"))


def fig_ablation(per_seed, out, det="LightGBM"):
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    ks = [0, 1, 3, 10, 30, 100]
    for i, (prefix, lab) in enumerate([("PA-HMMQ", "calibrated emissions"), ("PA-HMMQ[rawE", "probability emissions")]):
        for j, c in enumerate(["dev_test", "ext_pooled"]):
            ys, ss = [], []
            for k in ks:
                if prefix == "PA-HMMQ":
                    name = "PA-HMMQ" if k == 10 else f"PA-HMMQ[k={k}]"
                else:
                    name = "PA-HMMQ[rawE]" if k == 10 else f"PA-HMMQ[rawE,k={k}]"
                g = per_seed[(per_seed.detector == det) & (per_seed.estimator == name) & (per_seed.cohort == c)].mae_pp
                ys.append(g.mean()); ss.append(g.std())
            ax.errorbar(np.arange(len(ks)) + 0.06 * (2 * j - 1), ys, yerr=ss, color=SERIES[i], ls="-" if j == 0 else "--", marker="o", ms=4, lw=1.2,
                        capsize=2, label=f"{lab}, {COHORT_LABEL[c]}")
    ax.set_xticks(range(len(ks)), [str(k) for k in ks]); ax.set_xlabel("Prior strength κ (pseudo-transitions)"); ax.set_ylabel("MAE (pp)")
    ax.legend(fontsize=6); ax.set_title("Sensitivity to κ and emission model", loc="left")
    save(fig, os.path.join(out, "fig5_ablation_kappa"))


def fig_intervals(res, out, final, det="LightGBM"):
    I = pd.read_csv(os.path.join(res, "intervals.csv")); I = I[I.detector == det]
    I["cov"] = (I.true_burden >= I.lo - 1e-12) & (I.true_burden <= I.hi + 1e-12); I["w"] = (I.hi - I.lo) * 100
    meths = ["CC+conformal(const)", "PCC-iso+conformal(const)", "PA-HMMQ posterior 90% CrI", "PA-HMMQ+conformal(const)",
             "PA-HMMQ+conformal(norm)", "PA-HMMQ[rawE]+conformal(const)", "PA-HMMQ[rawE]+conformal(norm)"]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    for j, c in enumerate(COHORT_ORDER):
        for i, m in enumerate(meths):
            g = I[(I.method == m) & (I.cohort == c)].groupby("seed").agg(cov=("cov", "mean"), w=("w", "mean"))
            axs[0].errorbar(g["cov"].mean(), i + 0.15 * (j - 1.5), xerr=g["cov"].std(), fmt="o", ms=3.5, color=COHORT_COLOR[c], elinewidth=1,
                            label=COHORT_LABEL[c] if i == 0 else None)
            axs[1].errorbar(g.w.mean(), i + 0.15 * (j - 1.5), xerr=g.w.std(), fmt="o", ms=3.5, color=COHORT_COLOR[c], elinewidth=1)
    axs[0].axvline(0.9, color=TEXT2, ls="--", lw=1); axs[0].set_xlabel("Empirical coverage (target 0.90)")
    axs[1].set_xlabel("Mean interval width (pp)"); axs[1].set_xscale("log")
    axs[0].set_yticks(range(len(meths)), meths); axs[0].invert_yaxis(); axs[0].legend(fontsize=6, loc="lower left")
    save(fig, os.path.join(out, "fig6_intervals"))


def fig_strata(R, out, final, det="LightGBM"):
    bins = [-0.001, 0, 0.01, 0.10, 0.50, 1.0]; labels = ["0", "(0,1]", "(1,10]", "(10,50]", ">50"]
    x = R[(R.detector == det) & R.cohort.isin(EXT)].copy(); x["s"] = pd.cut(x.true_burden, bins, labels=labels)
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    for i, est in enumerate(["CC", "CC-MF", "HMM-src", final]):
        y = [x[(x.estimator == est) & (x.s == l)].groupby("seed").ae.mean().mean() for l in labels]
        ax.plot(range(len(labels)), y, marker="o", ms=4, lw=1.4, color=SERIES[i], label=EST_LABEL.get(est, est))
    ax.set_yscale("log"); ax.set_xticks(range(len(labels)), labels); ax.set_xlabel("Reference AF burden stratum (%)")
    ax.set_ylabel("MAE (pp, log scale)"); ax.legend(fontsize=6); ax.set_title("Error by burden stratum (pooled external)", loc="left")
    save(fig, os.path.join(out, "fig7_error_strata"))


def fig_error_ectopy(R, out, final, det="LightGBM"):
    x = R[(R.detector == det) & R.cohort.isin(EXT) & (R.estimator == final)].groupby(["patient", "cohort"]).agg(
        ae=("ae", "mean"), sv=("ectopy_sv", "first"), v=("ectopy_v", "first"), afl=("afl_burden", "first")).reset_index()
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6), sharey=True)
    for c in EXT:
        k = x.cohort == c
        axs[0].scatter(100 * (x.sv[k] + x.v[k]) + 1e-2, x.ae[k] + 1e-3, s=7, lw=0, alpha=0.6, color=COHORT_COLOR[c], label=COHORT_LABEL[c])
        axs[1].scatter(100 * x.afl[k] + 1e-2, x.ae[k] + 1e-3, s=7, lw=0, alpha=0.6, color=COHORT_COLOR[c])
    for a in axs: a.set_xscale("log"); a.set_yscale("log")
    axs[0].set_xlabel("Ectopic beats (% of beats, SV + V)"); axs[1].set_xlabel("Atrial flutter burden (%)")
    axs[0].set_ylabel("Absolute burden error (pp)"); axs[0].legend(fontsize=6)
    axs[0].set_title("A  Ectopy", loc="left"); axs[1].set_title("B  Atrial flutter", loc="left")
    save(fig, os.path.join(out, "fig8_error_analysis"))


def fig_forest(stats_json, out, final, det="LightGBM"):
    S = json.load(open(stats_json))
    t = S["tests"].get(f"{det}|{final}|ext_pooled", {})
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    names = list(t)
    for i, b in enumerate(names):
        v = t[b]
        ax.errorbar(v["mean_diff"], i, xerr=[[v["mean_diff"] - v["mean_ci"][0]], [v["mean_ci"][1] - v["mean_diff"]]], fmt="o", ms=4, color=SERIES[0], capsize=2)
        ax.text(1.02, i, f"p={v['p_holm']:.1g}", transform=ax.get_yaxis_transform(), fontsize=6, va="center", color=TEXT2)
    ax.axvline(0, color=TEXT2, lw=1); ax.set_yticks(range(len(names)), names); ax.invert_yaxis()
    ax.set_xlabel("Mean paired difference in AE (pp)\n(final PA-HMMQ − comparator; <0 favours PA-HMMQ)")
    ax.set_title("Pooled external cohorts", loc="left")
    save(fig, os.path.join(out, "fig9_forest"))


def fig_robustness(res, out):
    p = os.path.join(res, "robustness_results.csv")
    if not os.path.exists(p): return
    X = pd.read_csv(p); X["ae"] = (X.estimate - X.true_burden).abs() * 100
    conds = list(dict.fromkeys(X.condition))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    for a, det in zip(axs, ["LightGBM", "RRNet"]):
        for i, est in enumerate(["CC", "CC-MF", "HMM-src", "PA-HMMQ", "PA-HMMQ[rawE]"]):
            y = [X[(X.detector == det) & (X.estimator == est) & (X.condition == c)].groupby("seed").ae.mean() for c in conds]
            a.errorbar(np.arange(len(conds)) + 0.08 * (i - 2), [v.mean() for v in y], yerr=[v.std() for v in y], marker="o", ms=3, lw=1.2,
                       color=SERIES[i], capsize=1.5, label=EST_LABEL.get(est, est))
        a.set_xticks(range(len(conds)), conds, rotation=60, ha="right", fontsize=6); a.set_title(f"{det}, SHDB-AF", loc="left")
    axs[0].set_ylabel("MAE (pp)"); axs[0].legend(fontsize=5.5)
    save(fig, os.path.join(out, "fig10_robustness"))


def fig_efficiency(res, out):
    p = os.path.join(res, "efficiency.json")
    if not os.path.exists(p): return
    E = json.load(open(p))
    rows = [(k, v["seconds_per_24h_median"]) for k, v in E["components"].items()]
    fig, ax = plt.subplots(figsize=(3.6, 2.4))
    ax.barh(range(len(rows)), [r[1] * 1000 for r in rows], color=SERIES[0], height=0.6)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=6); ax.invert_yaxis(); ax.set_xscale("log")
    ax.set_xlabel("Milliseconds per 24-h recording (CPU, median)"); ax.set_title("Computational cost", loc="left")
    save(fig, os.path.join(out, "fig11_efficiency"))


def main(res, out):
    style.apply(); os.makedirs(out, exist_ok=True)
    R = pd.read_csv(os.path.join(res, "raw_results.csv")); R["ae"] = (R.estimate - R.true_burden).abs() * 100
    per_seed = pd.read_csv(os.path.join(res, "burden_metrics_per_seed.csv"))
    final = json.load(open(os.path.join(res, "statistics.json")))["final_method"]
    fig_method(out); fig_cohorts(R, out); fig_training(res, out); fig_roc_pr(res, out); fig_confusion(res, out)
    fig_main(per_seed, out); fig_bland_altman(R, out, final); fig_ablation(per_seed, out); fig_intervals(res, out, final)
    fig_strata(R, out, final); fig_error_ectopy(R, out, final); fig_forest(os.path.join(res, "statistics.json"), out, final)
    fig_robustness(res, out); fig_efficiency(res, out)
    print("figures done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", default="../results"); ap.add_argument("--out", default="../figures")
    a = ap.parse_args(); main(a.res, a.out)
