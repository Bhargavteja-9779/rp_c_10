# Review round 2 — Reviewer #2 (novelty, prior art, contribution differentiation)

Manuscript version reviewed: v1 + round-1 revisions. Focus: is the work incremental; is the gap genuine. Issues raised by Reviewer #1 are not repeated.

| # | Severity | Issue | Evidence | Required fix |
|---|---|---|---|---|
| 2.1 | MAJOR | **The effective method is an HMM detector/smoother, which has existed for >25 years.** Besides Moody & Mark (1983), an HMM AF detector was compared with entropy and variance detectors on ambulatory ECG in 1999 (Young, Brodnick, Spaulding, IEEE NNSP; doi:10.1109/NNSP.1999.788166), and HMM-based detection is reportedly used in commercial Holter software. The manuscript must not imply that temporal modelling of RR rhythm is a new idea. | Crossref-verified reference | Cite Young et al. 1999; state explicitly that the novelty lies in (a) evaluating aggregation strategies *for burden* (incl. prevalence-correction estimators) on three detectors and three external cohorts, (b) showing that per-patient prevalence correction adds nothing once temporal structure is modelled, and (c) conformal burden intervals. Remove any wording that presents the HMM itself as novel. |
| 2.2 | MAJOR | **Is the gap genuine?** If commercial systems already smooth temporally, "automated tools count windows" may be a straw man. | Introduction paragraph 2 | Qualify: many published research detectors and pipelines derive burden by counting or averaging windows (cite), while proprietary algorithms are undocumented; the study provides a transparent, reproducible comparison. |
| 2.3 | MODERATE | **Quantification framing vs result.** The paper motivates itself by quantification theory, but i.i.d. quantification estimators failed and the adaptive (prevalence-correcting) part added nothing. Readers may see the framing as unsupported. | Results "What drives the gain" | Keep the framing as the tested hypothesis, but state in Introduction/Discussion that the hypothesis was refuted for prevalence correction and that the benefit is temporal. Title already de-emphasises adaptation. |
| 2.4 | MODERATE | **Conformal novelty.** Split conformal regression is standard. | Methods | Specify the actual new element: normalisation of nonconformity by the HMM posterior burden SD and evaluation of external coverage for per-patient burden. |
| 2.5 | MINOR | **Comparability with previously reported burden errors** (e.g. median AE 1.3% in TAF-Tracker; bias −0.6 pp in Swiss-AF) is not discussed; differences in populations and metrics prevent direct comparison. | Discussion | Add a cautionary sentence. |
| 2.6 | MINOR | The word "novel" or claims of being "first" must be avoided unless supported. | full text | Search and remove. |

Recommendation: major revision (contribution must be repositioned as an evaluation/uncertainty study rather than a new detector).

---
# Author response and actions (round 2)

| # | Action | Status |
|---|---|---|
| 2.1 | Young et al. 1999 added (Crossref-verified); Introduction and Discussion state that HMM/Markov modelling of RR rhythm is established and specify the three contributions. | Fixed |
| 2.2 | Introduction qualified ("published research pipelines … proprietary algorithms are undocumented"). | Fixed |
| 2.3 | Introduction now states the hypothesis explicitly; Discussion first paragraph states that it was refuted for prevalence correction. | Fixed |
| 2.4 | Methods specify the normalised nonconformity score as the new element; Discussion reworded. | Fixed |
| 2.5 | Sentence added to "Comparison with previous work". | Fixed |
| 2.6 | Full-text search for "novel", "first", "unprecedented", "state-of-the-art": none in claims about this work after edit. | Checked |
