# What's New?

- In {{D:ext_total|patients}} external patients from Japan, China and Canada, a hidden Markov burden layer placed on top of RR-interval AF detectors reduced the mean absolute AF-burden error from {{bm:LightGBM|CC|ext_pooled|mae_pp}} to {{bm:LightGBM|PA-HMMQ[rawE]|ext_pooled|mae_pp}} percentage points compared with counting AF-classified windows, consistently across three detectors.
- The benefit came from modelling the temporal persistence of rhythm; classical prevalence-correction methods and per-patient re-estimation of rhythm dynamics did not help, and recalibrating window probabilities on the development population worsened burden estimates.
- False AF diagnoses in AF-free patients fell (specificity {{bm:LightGBM|CC|ext_pooled|present_30s_spec|2}} to {{bm:LightGBM|PA-HMMQ[rawE]|ext_pooled|present_30s_spec|2}}), with a reduction in sensitivity.
- Conformal intervals reached nominal 90% coverage of individual patients' burden in two of three external cohorts but under-covered in the third; atrial flutter remained the dominant source of error.
