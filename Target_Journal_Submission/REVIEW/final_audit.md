# Final consistency and reproducibility audit (Phases 34–35)

Generated after the last build (machine checks in `final_audit_checks.json`, produced by `manuscript/build/final_audit.py`).

## 1. Consistency audit (title ↔ abstract ↔ contributions ↔ method ↔ code ↔ experiments ↔ tables ↔ figures ↔ statistics ↔ conclusion)
| Check | Result |
|---|---|
| Strict build (every number in manuscript and supplement resolved from `results/*.json`, `tables/*.csv`; build fails on any missing value) | main: **True**, supplement: **True** |
| Data tokens resolved in main text | 168 |
| Main-text words (limit 5,000) | 4781 |
| References (limit 100); all verified via Crossref/DataCite/JSTOR/PhysioNet | 48; unverified: none |
| What's New bullets / words (≤150) | 4 / ≈134 |
| Keywords (3–6) | 6 |
| Missing figures / tables | none / none |
| Alt text under every figure legend | True |
| Supplementary tables/figures cited in main text | uncited tables: none; uncited figures: none |
| Claim "final PA-HMMQ < counting in all 9 detector × external-cohort combinations" | True |
| Claim "lowest error of the *pre-specified* estimators in each external cohort" (LightGBM) | lowest overall: {'ext_shdb-af': 'PA-HMMQ[rawE] (final)', 'ext_cpsc2021': 'PA-HMMQ[rawE] (final)', 'ext_icentia11k': 'HMM-src[rawE]', 'ext_pooled': 'HMM-src[rawE]'} — the post-hoc fixed-dynamics HMM with identical emissions is equal/marginally lower in Icentia11k and pooled; text states this |
| Claim "final lowest in all sensitivity settings (SHDB-AF, CPSC2021)" | True |
| Claim "final lowest in every robustness condition, both detectors" | True (18/18 conditions) |
| Amendment A1 decision recomputed by `analyze.py` | chosen = PA-HMMQ[rawE] (dev MAE 2.858 vs 3.186 pp) |
| Equations ↔ code | Verified line by line in review round 4 (`hmm.py`, `burden.py`, `conformal.py`) |
| Every experiment mentioned exists | Exp 1–3, 5: `run_main.py`; Exp 4: `run_robustness.py`, `run_sensitivity.py` (train fraction); Exp 6: `run_efficiency.py`; Exp 7: κ grid (`run_main.py` ablations), `run_sensitivity.py` (window length); Exp 8: `analyze.py` (error analysis); post hoc: `run_revision.py`, `local_recalibration.py`, `run_smoother_check.py` |
| Hand-typed numbers in sources | listed in `final_audit_checks.json`; all are design constants, literature values or counts verified against tables |

### Corrections made during the audit
* Robustness paragraph pre-written before the experiment ("errors increased with false R peaks…") contradicted the data and was rewritten from `table12_robustness.csv` (largest effect: 25-ms jitter; missed beats for RRNet).
* "Lowest error of all estimators" restricted to the pre-specified estimators (fair post-hoc comparator equivalent).
* Burden-stratum statement corrected (errors highest at >0–1% and >10%; calibrated emissions better above 50%).
* Interval figure/legends corrected (coverage below target in SHDB-AF; min–max bars on log axis).
* Efficiency re-measured on an idle machine: burden layer 261 ms, with interval sampling 283 ms, RR features 904 ms, LightGBM 7 ms, RRNet 119 ms per 24 h (earlier values were inflated by CPU contention).

## 2. Reproducibility audit (stranger's perspective)
| Question | Answer |
|---|---|
| Can I install it? | `pip install -r requirements.txt` (pinned versions) or `environment.yml`; Python 3.13; CPU only. |
| Can I obtain the data? | Yes: `python -m src.data.download` (public PhysioNet, no credentials; SHA-256 verified; Icentia11k subset sampled with a fixed seed). Licences in Table S1 (Icentia11k CC BY-NC-SA 4.0 → non-commercial use). |
| Can I preprocess / train / evaluate? | `python run_all.py --mode full` (≈4–6 h on 4 cores; steps resumable) or step-by-step commands in `code/README.md`. |
| Can I regenerate figures, tables and the exact manuscript numbers? | Yes: `analyze.py`, `local_recalibration.py`, `run_smoother_check.py`, `summarize_sensitivity.py`, `figures.py`, then `manuscript/build/build_manuscript.py` + `make_docx.js`. All manuscript numbers are tokens resolved from these outputs. |
| Is the configuration understandable? | `config/default.yaml` (pre-specified values) and `config/quick.yaml`. |
| Known sources of non-determinism | LightGBM multithreading (negligible); PyTorch deterministic mode on. |
| End-to-end test | `python run_all.py --mode quick --skip-download` executed on the final code. **First attempt failed** at the figure step (`dataset_summary.json` was written only to `../results`, never to the quick-mode results folder) — a genuine reproducibility bug. Fixed by passing output paths to `scripts/dataset_summary.py` and `scripts/leakage_audit.py` and adding the summary step to `run_all.py`; the re-run completed all steps ("All steps completed", 11 unit tests passed; log `results/experiment_logs/run_all_quick.log`). |
