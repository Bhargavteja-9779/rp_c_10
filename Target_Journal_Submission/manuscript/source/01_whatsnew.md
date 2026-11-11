# What's New?

- AF burden was estimated as a per-patient proportion (quantification) instead of by counting AF-classified windows, using a patient-adaptive hidden Markov model that works on top of any RR-interval AF detector.
- In {{D:ext_total|patients}} external patients from Japan, China and Canada, the method reduced the mean absolute burden error from {{bm:LightGBM|CC|ext_pooled|mae_pp}} to {{bm:LightGBM|PA-HMMQ[rawE]|ext_pooled|mae_pp}} percentage points and was the most accurate of nine estimators, consistently across three detectors.
- Distribution-free conformal intervals attained close to nominal 90% coverage in external cohorts, giving clinicians a per-patient statement of burden uncertainty.
- Atrial flutter and false burden in AF-free patients were the dominant remaining error sources.
