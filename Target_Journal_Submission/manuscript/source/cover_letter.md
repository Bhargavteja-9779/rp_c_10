[Date]

Professor [Name], Editor-in-Chief, *EP Europace*
European Heart Rhythm Association / Oxford University Press

Dear Editor,

We submit the manuscript entitled "{{title}}" for consideration as a Clinical Research Article in *EP Europace*.

Atrial fibrillation (AF) burden is becoming a key descriptor for risk stratification and therapy evaluation, and it is now almost always computed automatically from Holter, patch or wearable recordings. Current tools derive burden by counting time windows classified as AF and report no uncertainty. In this study we treated burden as a per-patient quantity to be estimated, combined a temporal (hidden Markov) burden layer that can be placed on top of any RR-interval AF detector with distribution-free conformal intervals, and evaluated it with three detectors in {{D:ext_total|patients}} external patients from Japan, China and Canada who were never used for model development or calibration.

The main findings are: (i) the burden layer reduced the mean absolute per-patient burden error in the pooled external cohorts from {{bm:LightGBM|CC|ext_pooled|mae_pp}} to {{bm:LightGBM|PA-HMMQ[rawE]|ext_pooled|mae_pp}} percentage points relative to classify-and-count, and raised specificity for AF presence from {{bm:LightGBM|CC|ext_pooled|present_30s_spec|2}} to {{bm:LightGBM|PA-HMMQ[rawE]|ext_pooled|present_30s_spec|2}}; (ii) the improvement was due to temporal modelling, whereas the pre-registered specification, per-patient re-estimation of rhythm dynamics and classical prevalence-correction methods did not help—negative results we report in full; (iii) conformal intervals reached nominal coverage in two of three external cohorts, with under-coverage in the third; and (iv) atrial flutter remained the dominant source of error. We describe the effect size as modest and discuss the limitations openly.

We believe the work fits the journal's scope in arrhythmia diagnostics, digital health and artificial intelligence in electrophysiology. The study follows TRIPOD+AI and the 2025 EHRA/HRS/ESC e-Cardiology scientific statement on AI in clinical electrophysiology; the completed EHRA AI checklist is uploaded as a separate supplementary file. The analysis plan was pre-registered in version control before model training, deviations are reported, and all code and per-patient result files that regenerate every number, table and figure will be made publicly available.

**Use of artificial-intelligence tools.** In line with the journal's policy, we disclose that a large language model-based assistant (Claude, Anthropic) was used to write analysis code, run the experiments and draft the manuscript. The authors [to be confirmed by the authors] verified the analyses and take full responsibility for the content. No AI tool is listed as an author.

The manuscript is original, has not been published previously, and is not under consideration for publication elsewhere. All authors have approved the submission [to be confirmed]. The study used only publicly available, de-identified databases; no new ethical approval was required. [Conflict-of-interest statement and funding to be completed by the authors.] [If any author is an editor of EP Europace, state it here.]

[Suggested reviewers, optional]

Yours sincerely,

[Corresponding author name, degrees]
[Affiliation, postal address, e-mail, telephone]
On behalf of all authors
