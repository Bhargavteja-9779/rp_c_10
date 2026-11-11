# Review round 4 — Reviewer #4 (ML methodology, optimisation, implementation correctness; code inspected)

Code inspected: `src/models/{hmm,burden,detectors,conformal}.py`, `src/preprocessing/{windows,features}.py`, `experiments/run_main.py`, `config/default.yaml`. Each Methods/Supplement statement was checked against the code; matches are listed at the end. Only discrepancies/omissions are raised.

| # | Severity | Issue (code ↔ manuscript) | Location | Fix |
|---|---|---|---|---|
| 4.1 | MODERATE | EMQ is run on **isotonic-recalibrated** posteriors with the duration-weighted source prior; the manuscript does not say so. | `burden.py: estimate()` | Document in Supplement S4. |
| 4.2 | MODERATE | The MAP-EM convergence test uses the **summed log-likelihood over all patients**, not a per-patient criterion (max 50 iterations). | `hmm.py: BurdenHMM.infer` | Document; note low impact (κ-insensitivity). |
| 4.3 | MODERATE | Windows on either side of an invalid RR interval within a recording are treated as **adjacent** in the HMM. | `windows.py`, `burden.py:_seq_index` | Document (valid intervals ≈100% in all databases). |
| 4.4 | MODERATE | The "COSEn-type" feature is SampEn(m=2, r=0.2·SD) + ln(0.06) − ln(mean RR), i.e. a hybrid: the original COSEn uses a fixed tolerance in the SampEn itself. The Supplement wording is imprecise. | `features.py` | Describe exactly. |
| 4.5 | MINOR | Incomplete windows (<60 valid RR) at the end of runs are excluded from both reference and estimated burden; "analysed time" should be defined accordingly. | `windows.py` | Define analysed time in Methods. |
| 4.6 | MINOR | MITDB paced records are retained (non-AF). | `records.py` | Mention in Supplement S2. |
| 4.7 | MINOR | LightGBM uses 4 threads without `deterministic=True`; tiny run-to-run differences are possible. PyTorch runs with deterministic algorithms. | `detectors.py` | State in README/Supplement. |
| 4.8 | MINOR | `TemperedEmission` and `RawEmission` implement e(AF) ∝ σ(logit p / T), e(non-AF) ∝ 1 − σ(·); consistent with the Methods formula (likelihood ratio (p/(1−p))^(1/T)). | `burden.py` | none |

Verified matches (no action): ε = 0.002; α = 0.10; 200 FFBS samples at converged parameters; κ = 10 pseudo-transitions per row + same prior on initial distribution; add-one smoothed source transitions from calibration-A window labels; 50-bin Laplace-smoothed histograms on logit(p) ∈ [−14, 14]; window label ≥50 % AF time; CC threshold 0.5; CC-MF median filter of length 3 within sequences; ACC/PACC with duration-weighted calibration-A rates and clipping to [0,1]; conformal quantile ⌈(n+1)(1−α)⌉ on calibration-B patients; RRNet architecture/optimiser/early stopping; LightGBM hyper-parameters and early stopping on inner validation; ≥30 s presence rule = estimated burden × analysed hours × 3600 ≥ 30.

Recommendation: minor revision (documentation), no re-analysis needed.

---
# Author response (round 4)
4.1–4.7 documented in Methods ("analysed time" definition) and Supplement S2–S4; README notes LightGBM thread nondeterminism. No code changed after results were generated (to keep results reproducible from the archived code).
