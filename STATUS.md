# Pipeline status (for resumption)
- Phase 0 journal selection: DONE (EP Europace, OUP) -> Target_Journal_Submission/journal_selection/
- Phases 1-5 topic, prior art, preregistration: DONE -> supplementary/S1_research_design_preregistration.md (+ Amendment A1)
- Data: annotation files downloaded (code/data/raw, gitignored; re-download: `python -m src.data.download`), caches W60 built.
- Main experiment: RUNNING/see results/experiment_logs/main_full.log (`python experiments/run_main.py --config config/default.yaml --out ../results`)
- Next: robustness (experiments/run_robustness.py), train-fraction & window-length sensitivity, efficiency, analysis/figures/tables, manuscript, 10 reviews, DOCX, cover letter.
