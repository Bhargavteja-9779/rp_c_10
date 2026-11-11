# AF burden as per-patient quantification — reproducible code

Code for the manuscript *"Estimating atrial fibrillation burden as a per-patient quantification problem with
distribution-free uncertainty intervals: development and multinational external validation"* (target: EP Europace).

It trains three window-level AF detectors on RR intervals (Classical-LR, LightGBM, RRNet), estimates per-patient
AF burden with nine estimators including the proposed **patient-adaptive hidden Markov quantifier (PA-HMMQ)**, builds
split-conformal burden intervals, and evaluates everything in a US development pool and three external cohorts
(SHDB-AF Japan, CPSC2021 China, Icentia11k Canada). Every number, table and figure in the manuscript is generated
by the scripts below from machine-readable result files.

## 1. Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # or: conda env create -f environment.yml
```
Tested with Python 3.13 on Linux, CPU only (4 cores, 15 GB RAM). CUDA and Apple-Silicon MPS are detected
automatically (`src/models/detectors.py:get_device`) but were not used for the reported results.

## 2. Data
All data are public on PhysioNet; only annotation (`.atr`, `.qrs`, `.ecg`) and header files are needed (~2 GB incl. the
Icentia11k subset). Downloads are verified against PhysioNet SHA-256 checksums.
```bash
python -m src.data.download --root data/raw          # all 9 databases; Icentia11k: 800 random patients (seed 20261110), 10 segments each
python -m src.data.dataset --W 60                     # parse annotations -> RR windows -> 16 features (cached in data/processed)
python scripts/leakage_audit.py                       # duplicate/near-duplicate and split-disjointness audit -> results/leakage_audit.json
python scripts/dataset_summary.py                     # Table 1 / Table S1 and results/dataset_summary.json
```
Licences: PhysioNet databases under their respective licences (ODC-By for most; see each `LICENSE.txt` downloaded with
the data). Known data issues handled in code: SHDB-AF record 020 is an exact duplicate of 005 and is excluded
(`src/data/records.py:EXCLUDE`); SHDB-AF metadata columns are `Data_ID`/`Subject_ID`; CPSC2021 patient-51 files
return HTTP 404 and are absent.

## 3. One-command reproduction
```bash
python run_all.py --mode quick    # pipeline check: 1 seed, 2 RRNet epochs, 40-patient external subsets (~20-30 min)
python run_all.py --mode full     # full study as reported (≈4-6 h on a 4-core CPU)
```
Outputs: `../results/` (raw per-patient results, metrics.json, statistics.json, logs, saved models),
`../tables/` (CSV + Markdown), `../figures/` (PNG + TIFF, 300 dpi).

## 4. Individual steps
| Step | Command | Output |
|---|---|---|
| Main experiments (Exp 1-3, 5) | `python experiments/run_main.py --config config/default.yaml --out ../results` | raw_results.csv, intervals.csv, window_metrics.csv, curves.csv, models/ (resumable) |
| Robustness (Exp 4) | `python experiments/run_robustness.py --out ../results` | robustness_results.csv, robustness_intervals.csv |
| Training size / window length (Exp 4b, 7b) | `python experiments/run_sensitivity.py --res ../results` (needs `python -m src.data.dataset --W 30` and `--W 120`) | results/sensitivity/*/ |
| Efficiency (Exp 6) | `python experiments/run_efficiency.py --res ../results` | efficiency.json |
| Statistics + tables | `python experiments/analyze.py && python experiments/summarize_sensitivity.py` | ../tables, metrics.json, statistics.json |
| Figures | `python -m src.visualization.figures` | ../figures |
| Unit tests | `python -m pytest -q tests` | — |
| Manuscript | `cd ../manuscript/build && python build_manuscript.py && node make_docx.js manuscript.json ../Final_Manuscript.docx` | DOCX with all numbers resolved from results |

## 5. Configuration
`config/default.yaml` holds every pre-specified setting (seeds 11/22/33/44/55, splits 45/15/20/20 %, κ = 10,
α = 0.10, 200 posterior samples, detector hyper-parameters). The pre-registration and its single amendment are in
`../supplementary/S1_research_design_preregistration.md`.

## 6. Code map
```
src/data/download.py       PhysioNet downloader (annotations only, SHA-256 verified)
src/data/records.py        annotation parsing -> RR series with per-beat rhythm labels
src/data/dataset.py        window caches
src/preprocessing/         windows, RR features, perturbations (robustness)
src/models/detectors.py    Classical-LR, LightGBM, RRNet
src/models/hmm.py          vectorised 2-state HMM, MAP-EM, forward-filtering backward-sampling
src/models/burden.py       CC, CC-MF, PCC, PCC-iso, ACC, PACC, EMQ, HMM-src, PA-HMMQ
src/models/conformal.py    split-conformal burden intervals
src/training/splits.py     stratified patient-level splits
src/evaluation/metrics.py  window and patient metrics
src/statistics/tests.py    Wilcoxon, Holm, McNemar, Clopper-Pearson, bootstrap
src/visualization/         figures
experiments/               experiment drivers and analysis
scripts/                   leakage audit, dataset summary
tests/                     unit tests
```
