# Review round 6 — Reviewer #6 (computational complexity, latency, memory, scalability, deployment feasibility)

| # | Severity | Issue | Evidence | Required fix |
|---|---|---|---|---|
| 6.1 | MAJOR | **Timing measurements are not trustworthy**: `efficiency.json` was produced while other experiments were running (load average >6 on 4 cores); e.g. RR-feature extraction 797 ms and RRNet inference ≈12.8 s per 24 h are implausibly slow. | efficiency.json; system load log | Re-run on an otherwise idle machine after all experiments; report hardware, threads and medians over recordings. |
| 6.2 | MODERATE | **No complexity statement.** Forward–backward is O(T·S²) per EM iteration (S = 2 states), FFBS O(K·T) for K samples; the vectorised implementation pads sequences to the longest length, so memory is O(N_seq·T_max). | `hmm.py` | Add to Supplement S4; report measured peak memory. |
| 6.3 | MODERATE | **Scalability to 14-day patches and implantable monitors.** Cost is linear in recording length; but implantable loop recorders store episodic electrograms, not continuous RR series, so the method applies only where continuous RR data exist. | Discussion | State scope. |
| 6.4 | MODERATE | **Is the benefit worth the cost?** Counting costs microseconds; the HMM layer costs a fraction of a second per 24 h — negligible relative to detector inference and report generation. | efficiency (after re-run) | State in Results/Discussion with the idle-machine numbers. |
| 6.5 | MINOR | Energy consumption not measured; GPU not used. | — | State as limitation of the efficiency analysis (CPU wall-clock only). |
| 6.6 | MINOR | Number of FFBS samples (200) governs the Monte-Carlo error of σ̂; not varied. | Methods | Mention; σ̂ only scales the conformal score, whose quantile is calibrated empirically. |

---
# Author response (round 6)
* 6.1 — efficiency re-run after all experiments on an idle machine (see final_audit.md for the final numbers; manuscript tokens read `results/efficiency.json`).
* 6.2 — complexity and memory statement added to Supplement S4 (peak traced Python memory of the burden layer with FFBS reported from `efficiency.json`).
* 6.3–6.6 — Discussion/Supplement sentences added.
