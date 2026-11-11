# Review round 5 — Reviewer #5 (dataset validity, generalisation, domain shift, external validity, deployment)

Goal: try to invalidate the central claims. New issues only.

| # | Severity | Issue / attack | Evidence checked | Outcome / required fix |
|---|---|---|---|---|
| 5.1 | MAJOR | **Is the gain an artefact of one cohort (Icentia11k dominates the pooled endpoint)?** | Per-cohort, per-detector MAE (9 detector × cohort combinations) | Attack failed: the final PA-HMMQ had lower mean error than counting in all 9 combinations. Make this explicit in Results. |
| 5.2 | MAJOR | **Interval validity under shift.** Coverage 0.84 in SHDB-AF; in AF patients 0.89 pooled. A clinician would need to know whether the problem is fixable with modest local data. | Table 5 | Run a local-recalibration experiment (new). |
| 5.3 | MODERATE | **Reference R peaks.** Several databases provide manually reviewed beats; in deployment, automatic detection errors occur. AFDB and SHDB-AF use automatic R peaks, which partly answers this; robustness simulations cover the rest. | Methods; Fig. 5 | State explicitly which cohorts use automatic R peaks (done in Methods) and link to the robustness results. |
| 5.4 | MODERATE | **Label quality of the large external cohort** (Icentia11k technologist labels; atrial flutter labels with irregular RR). | Error analysis | Already handled by AF+AFL analysis; add caution in Limitations (present). |
| 5.5 | MODERATE | **Deployment mode.** The HMM uses the whole recording (forward–backward); it is an offline post-processing step, not real-time detection. | Methods | State in Discussion (clinical implications). |
| 5.6 | MINOR | **Population differences** (SHDB-AF: all paroxysmal AF; Icentia11k: outpatients referred for monitoring; development: mixed) affect prevalence-dependent metrics. | Table 1 | Mention in Limitations. |

---
# Author response (round 5)

* **5.1** Results now state that the reduction vs counting occurred in all nine detector × external-cohort combinations (machine-checked from `raw_results.csv`).
* **5.2 New experiment** (`experiments/local_recalibration.py` → `tables/table18_local_recalibration`, `statistics.json: local_recalibration`): recomputing the conformal quantile from 10, 20 or 40 randomly chosen, locally labelled patients of each external cohort (200 repeats per seed) restored mean marginal coverage to ≈0.90 in every cohort, but coverage varied between draws (5th percentile ≈0.72–0.82), coverage in AF patients remained below nominal (≈0.80–0.89), and in SHDB-AF intervals widened substantially. Reported in Results and Discussion as post hoc.
* **5.3–5.6** text added (Methods already lists automatic R-peak cohorts; Discussion: offline use; Limitations: population differences).
