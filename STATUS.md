# Pipeline status (for resumption after interruptions)
Last update: 2026-11-11 03:07 UTC
- DONE: journal selection (EP Europace), pre-registration (+A1, +R1), data download/caches (W60, W30; W120 building),
  leakage audit (SHDB-AF dup removed), unit tests, manuscript sources/builder/DOCX renderer, EHRA checklist, cover letter draft.
- RUNNING (restart if killed; all resumable/skip-done):
  1. `cd Target_Journal_Submission/code && python experiments/run_main.py --config config/default.yaml --out ../results` (resume supported)
  2. `python experiments/run_sensitivity.py --res ../results --only trainfrac_25 trainfrac_50 window_30` (rerun restarts unfinished variants)
  3. `python -m src.data.dataset --W 120 --dbs ltafdb afdb mitdb nsrdb nsr2db chfdb shdb-af cpsc2021`
- NEXT after main: `python experiments/run_revision.py` (R1) -> `python experiments/run_robustness.py` -> `run_sensitivity.py --only window_120`
  -> `run_efficiency.py` (on idle machine) -> `analyze.py` -> `summarize_sensitivity.py` -> figures -> build manuscript
  (`cd manuscript/build && python build_manuscript.py && python build_manuscript.py layout_supp.json && node make_docx.js ...`)
  -> 10 review rounds (REVIEW/) -> final audit -> risk report.
