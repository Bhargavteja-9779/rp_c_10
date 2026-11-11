"""EHRA AI checklist (Svennberg et al., Europace 2025;27:euaf071, Table 2) mapped to this manuscript.
Item wording is abbreviated from the published Explanation column; see the original statement for full text."""
import json, os
ITEMS = [
 ("i", "Title", "Identify the study as using AI/machine learning", "Title (\"quantification\", \"distribution-free\"); Abstract Methods name the machine-learning detectors and the hidden Markov quantifier. Authors may wish to add \"artificial intelligence\" to the title."),
 ("1", "Intended clinical use", "Intended use, place in workflow, objective", "Introduction (last paragraph); Discussion – Clinical implications: post-processing layer for automated burden from Holter/patch/wearable RR series."),
 ("2", "Clinical benefit", "Added benefit vs standard care/gold standard", "Introduction; Results – Burden estimation; Discussion – Clinical implications and Limitations (benefit on decisions not tested)."),
 ("3", "Data collection", "How data were collected", "Methods – Data sources; Supplementary Table S1; original database publications cited."),
 ("4", "Source of data", "Study design / source of input data", "Methods – Study design and Data sources (retrospective, public PhysioNet databases)."),
 ("5", "Development data set", "Describe the training data set", "Methods – Data sources; Table 1; Supplementary Table S1."),
 ("6", "Participants", "Participants and eligibility criteria", "Methods – Data sources and Reference standard (exclusions: invalid RR, unlabelled rhythm, duplicate recording); Table 1. Individual-level demographics not available for most public databases (limitation)."),
 ("7", "Comparator / gold standard", "Definition and limitations of ground truth", "Methods – Reference standard (database rhythm annotations; AFL counted as non-AF with AF+AFL sensitivity analysis); Discussion – Limitations (annotation quality)."),
 ("8", "Testing data set", "Testing set and split definition", "Methods – Data partitioning (patient-level stratified splits, five seeds) and external cohorts never used for training/calibration."),
 ("9", "Sample size", "How study size was arrived at", "All available annotated patients in each database; Icentia11k random 800-patient subset (computational constraint) – Methods – Data sources; no formal sample-size calculation (limitation)."),
 ("10", "Outcome", "Standardised, reproducible, clinically relevant outcome", "Methods – Endpoints: per-patient absolute AF-burden error (pp); secondary agreement, threshold classification, coverage."),
 ("11", "Data type", "Data type incl. pre-processing", "Methods – Reference standard and units (RR intervals from beat annotations, 0.2–3.0 s, 60-beat windows); Supplementary S2–S3."),
 ("12", "Data preparation / leakage", "Input handling, augmentation, leakage prevention", "Methods – Data partitioning and leakage control; Supplementary S2 (automated duplicate audit; per-window features; calibration sets disjoint). No augmentation used."),
 ("13", "Balanced groups", "How/if groups were balanced", "Splits stratified by database and AF presence (Methods); no class re-weighting or resampling of windows."),
 ("14", "Data issues", "Poor-quality/noisy/missing/duplicate data", "Methods – Reference standard (implausible RR excluded); Supplementary S2 (missing CPSC2021 patient-51 files; duplicate SHDB-AF recording removed; unlabelled Icentia11k segments excluded); robustness to simulated R-peak errors (Results; Figure 5)."),
 ("15", "Feature engineering", "Feature selection and who extracted features", "Supplementary S3 (16 RR features computed automatically by the authors' code; no data-driven feature selection)."),
 ("16", "Legal framework", "Regulatory approval status", "Research software, not approved as a medical device (to be stated by authors in cover letter/Methods if required)."),
 ("17", "Explainability", "Patient-level / global / local explainability", "The burden layer is a transparent two-state Markov model with interpretable per-patient transition probabilities; posterior burden and interval are reported per patient (Methods; Supplementary S4). Detectors use interpretable RR features (Classical-LR, LightGBM) or a neural network (RRNet)."),
 ("18", "Ethical approval", "Ethics information", "Methods – Ethics (public de-identified data; original approvals in cited publications)."),
 ("19", "Fairness", "Inclusion of relevant groups", "External cohorts from Japan, China and Canada; sex and age subgroups in SHDB-AF (Supplementary Table S12); limited demographic metadata elsewhere (limitation)."),
 ("20", "Data availability / code sharing", "Public data and code", "Data availability statement: all databases public; full code and per-patient results publicly available."),
 ("21", "Trial registration", "Registration if a trial", "Not applicable (retrospective diagnostic-accuracy study); analysis plan pre-registered in version control (Supplementary S1)."),
 ("22", "Participants (results)", "Baseline characteristics of internal and external data", "Results – Cohorts; Table 1; Supplementary Figure S1."),
 ("23", "Training performance", "Results in training data", "RRNet learning curves (Supplementary Figure S4); calibration-B (in-distribution) burden and interval results (Supplementary Table S5)."),
 ("24", "Internal validation", "Results in testing data", "Development test set results (Table 2, Table 5, Supplementary Table S2)."),
 ("25", "External validation", "Results in external data", "SHDB-AF, CPSC2021, Icentia11k (Tables 2–5; Figures 2–6)."),
 ("26", "Model performance metrics", "Appropriate metrics", "Window AUROC/AUPRC/sensitivity/specificity/ECE; burden MAE, bias, LoA, CCC, threshold sensitivity/specificity, interval coverage/width."),
 ("27", "Performance errors", "Error analysis", "Results – Error analysis; Figure 6; Supplementary Tables S6, S8, S13; Supplementary Figure S7."),
 ("28", "Comparison with classic statistical methods", "What did the model add?", "Eight comparators including classical counting, smoothing and statistical quantification estimators (Table 4); classical logistic-regression detector."),
 ("29", "Generalizability", "Discussion of generalisability", "Discussion – Interpretation, Comparison with previous work and Limitations."),
 ("ii", "Conclusion", "Supported by the data?", "Conclusions restricted to the measured endpoints; effect size described as modest."),
]
doc = {"title": "EHRA AI checklist — completed for: Estimating atrial fibrillation burden as a per-patient quantification problem with distribution-free uncertainty intervals",
       "paragraphs": ["Checklist from: Svennberg E, Han JK, et al. State of the Art of Artificial Intelligence in Clinical Electrophysiology in 2025. Europace 2025;27(5):euaf071 (Table 2). Item descriptions are abbreviated; the right-hand column states where each item is addressed in the manuscript. Page numbers to be added by the authors after final typesetting of the submission file.",
                      "Reporting standard stated in Methods: TRIPOD+AI and the EHRA AI checklist."],
       "tables": [{"caption": "", "header": ["Item", "Section/topic", "Requirement (abbreviated)", "Where addressed"], "widths": [700, 1900, 2800, 4238],
                   "rows": [list(r) for r in ITEMS]}]}
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "EHRA_AI_checklist.json")
json.dump(doc, open(out, "w"), indent=1)
print(out)
