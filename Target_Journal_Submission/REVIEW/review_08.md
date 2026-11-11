# Review round 8 — Reviewer #8 (competing researcher who built a similar RR-based burden pipeline)

Aim: show that the contribution is incremental, that a simpler existing method achieves the same, that the gain is caused by another factor, or that comparisons are unfair.

| # | Severity | Critique | Test performed | Result |
|---|---|---|---|---|
| 8.1 | MAJOR | "Your HMM is just a smoother. The CC-MF baseline used an arbitrarily short 3-window filter; a properly tuned median filter would match it." | **New post-hoc experiment** (`experiments/run_smoother_check.py`): median-filter lengths 3/5/7/9/15 windows, LightGBM, 5 seeds; length selected on development patients only (calB ∪ dev_test) → 7 windows; external evaluation afterwards. | Critique **largely valid**: the dev-selected 7-window filter reduced pooled external error to 2.63 pp versus 2.52 pp for the final PA-HMMQ (mean paired difference −0.11 pp, 95% CI −0.15 to −0.07); a 15-window filter (not selectable on development data) reached 2.56 pp. The accuracy advantage of the HMM over a tuned smoother is therefore small. The HMM's distinct advantage is a posterior distribution, which the conformal intervals require. |
| 8.2 | MAJOR | "The deep baseline is a re-implementation, not ArNet2; you may have weakened it." | Code/manuscript check | RRNet is labelled a re-implementation throughout; window AUROC 0.99 in Icentia11k and CPSC2021 indicates it is not a weak model. ArNet2 weights were not used. Limitation retained. |
| 8.3 | MODERATE | "The pooled endpoint favours methods that suppress false positives because Icentia11k is mostly AF-free." | Per-cohort tables | Improvement present in every cohort and detector (round 5); stated. |
| 8.4 | MODERATE | "Prevalence correction never mattered; why keep 'patient-adaptive' in the method's name?" | Ablation | Name kept because it is the pre-registered method; manuscript states that the adaptive component can be omitted (HMM-src with the same emissions performs identically). |

---
# Author response (round 8)
* 8.1 — Results ("What drives the gain") and Discussion now report the tuned-median-filter comparison (Supplementary Table S19) and state that most of the accuracy gain is obtainable with a tuned smoother, whereas the HMM additionally provides the posterior needed for calibrated intervals. Abstract/What's New/Conclusions adjusted to avoid implying a large accuracy advantage over smoothing.
* 8.2–8.4 — wording checked; Discussion states that the adaptive component can be omitted.
