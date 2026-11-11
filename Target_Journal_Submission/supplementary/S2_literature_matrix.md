# S2 — Literature matrix and gap analysis

Scope note: every reference was verified bibliographically (Crossref/DataCite/JSTOR; see `manuscript/refs/verified_references.json`).
Content columns are restricted to what was actually read: **[A]** = abstract read in full (PubMed), **[S]** = title/search
snippet only, **[K]** = established method paper cited for its method only. Cells that could not be verified are "n.v.".
No full texts behind paywalls were accessed.

| Paper | Year | Venue | Problem | Data / size | Method | Evaluation & generalisation | Uncertainty reported | Code | Gap relative to this study | Src |
|---|---|---|---|---|---|---|---|---|---|---|
| Chocron et al. | 2021 | IEEE TBME | AF burden from long single-channel ECG | n.v. (abstract not read) | ArNet: deep RNN on RR intervals | External test set (per snippet) | n.v. | n.v. | point estimate only | [S] |
| Biton et al. (ArNet2) | 2023 | npj Digit Med | AF event detection from RR, generalisation across geography/age/sex | 2,147 pts / 51,386 h development; 402 pts test (USA, Israel, Japan, China); 1,825 Holters validation | Recurrent DL on beat-to-beat intervals | Multi-centre external; subgroup analysis; AFL identified as main failure mode | not reported in abstract | n.v. | burden as by-product; no bias correction or per-patient interval | [A] |
| Haekal et al. | 2026 | Physiol Meas | AF detection + burden from RR; calibration under shift | public Holter DBs (record-wise CV + external) | interpretable RR-feature model; probability vs hard-label burden; Platt/isotonic recalibration | external calibration deteriorated; recalibration with **target labels** improved probability burden | calibration metrics; no intervals | n.v. | requires labelled target data; no temporal model; no per-patient interval | [A] |
| Karimizadeh et al. (TAF-Tracker) | 2026 | Heart Rhythm O2 | AF detection/burden on textile ECG | public AF DBs + 47 AF patients 14-day textile ECG | RR features + RF/XGBoost/SVM/LR on 60-beat segments | subject-wise split; burden median AE 1.3% | no | n.v. | single device; no uncertainty; no quantification | [A] |
| Hennings et al. | 2023 | CVDHJ | AI vs manual burden, Swiss-AF 7-day Holter | 100 Holters / 82 pts | commercial AI (Cardiomatics) | Bland–Altman bias −0.006, LoA −0.042 to 0.030 | no | proprietary | single cohort; closed algorithm | [A] |
| Aguilar et al. | 2026 | Europace | smartwatch AF detection/burden after ablation vs ICM | n.v. | commercial smartwatches | correlation r > 0.97 with ICM burden (snippet) | n.v. | proprietary | PPG/watch; not RR-Holter | [S] |
| Abbasi et al. | 2026 | Heart Rhythm | conformal coverage of AI-ECG AF classifier under shift | PTB-XL → Chapman-Shaoxing, Georgia (12-lead) | split conformal, local recalibration, risk control | coverage fell to 0.72–0.76 externally; restored with local labels | yes (classification sets) | n.v. | classification of single ECGs, not burden | [A] |
| El Allam & Hamlich | 2026 | Physiol Meas | per-class conformal FNR control, multi-label ECG | PTB-XL, Chapman | exact-binomial risk control | coverage fell under shift (94.3%→45.5%) | yes | n.v. | not burden | [A] |
| Dash et al. | 2009 | Ann Biomed Eng | real-time AF detection | n.v. | RMSSD, Shannon entropy, turning-point ratio | n.v. | no | – | window-level only | [K] |
| Lake & Moorman | 2011 | AJP Heart | AF detection by entropy (COSEn) | n.v. | coefficient of sample entropy | n.v. | no | – | window-level only | [K] |
| Tateno & Glass | 2001 | MBEC | AF detection by RR/ΔRR histograms | n.v. | KS test on ΔRR density | n.v. | no | – | window-level only | [K] |
| Petrėnas et al. | 2015 | Comput Biol Med | low-complexity AF detection, long-term monitoring | n.v. | RR irregularity + ectopy suppression | n.v. | no | – | window-level only | [K] |
| Andersen et al.; Faust et al. | 2019; 2018 | ESWA; Comput Biol Med | DL AF detection from RR | n.v. | CNN-LSTM / LSTM on RR | n.v. | no | n.v. | window-level only | [K] |
| Forman; Saerens et al.; Bella et al. | 2008; 2002; 2010 | DMKD; Neural Comput; ICDM | class-prevalence estimation (quantification) under prior shift | generic | ACC; EM prior adjustment; PACC | – | – | – | assume i.i.d. samples; never applied to AF burden (searches 2026-11-10) | [K] |

## Gap analysis (Phase 3)
* **What exists:** accurate RR-based AF detectors with multi-centre generalisation (ArNet2), burden agreement studies for commercial and feature-based tools, label-requiring recalibration of probability-based burden (Haekal 2026), and conformal methods for single-ECG classification.
* **What it fails to address:** (i) burden is estimated by counting/averaging window outputs, a biased prevalence estimator; (ii) no per-patient uncertainty for burden; (iii) no label-free correction for patient-specific prevalence; (iv) no systematic comparison of quantification estimators for burden.
* **Why it matters:** burden thresholds and changes are used clinically; errors and their uncertainty determine whether a low burden is real.
* **What this research adds (as finally supported by the data):** a systematic, multinational comparison of nine burden estimators on three detectors; evidence that a temporal (HMM) burden layer reduces error while classical i.i.d. quantification estimators and source probability recalibration do not; evidence that patient-level re-estimation of dynamics adds no measurable benefit; posterior-normalised conformal burden intervals with external coverage assessment; identification of atrial flutter and AF-free false burden as dominant residual errors.
* **How verified:** Experiments 1–8 (see S1), paired tests at patient level, five seeds.
