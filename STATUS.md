# Pipeline status (for resumption after interruptions)
Last update: 2026-11-11 08:03 UTC
- DONE: journal selection; pre-registration (+A1, R1 amendment); data; leakage audit; main 5-seed experiment;
  sensitivity (trainfrac 25/50, window 30/120); smoother check; local recalibration; manuscript sources rewritten to
  final evidence; reviews 01–09 written (REVIEW/); graphical abstract; EHRA checklist; cover letter draft.
- RUNNING: `cd Target_Journal_Submission/code && python experiments/run_revision.py` (R1, not resumable; rerun fully if killed)
  then `python experiments/run_robustness.py --out ../results --detectors LightGBM RRNet --procs 3`.
- AFTER THEY FINISH (in this order):
  1. `python experiments/run_efficiency.py` (idle machine)
  2. `python experiments/analyze.py && python experiments/local_recalibration.py && python experiments/run_smoother_check.py && python experiments/summarize_sensitivity.py && python scripts/dataset_summary.py && python -m src.visualization.figures`
  3. Update R1/robustness sentences in manuscript/source/04_results.md from tables 12/13/15
  4. `cd ../manuscript/build && python final_audit.py` (strict build) → `node make_docx.js manuscript.json ../Final_Manuscript.docx`, supplement, cover letter, EHRA checklist; render PDF; inspect pages
  5. review_10.md (final adversarial), final_audit.md, rejection_risk_report.md; un-ignore results/ in .gitignore and commit final results.
