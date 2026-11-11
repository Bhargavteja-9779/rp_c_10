# Submission package — EP Europace (Oxford University Press)

**Manuscript:** *Temporal quantification of atrial fibrillation burden with distribution-free uncertainty intervals: development and multinational external validation* (Clinical Research Article).

| Folder | Contents |
|---|---|
| `journal_selection/` | `selected_journal.md` (target journal record), `journal_comparison.md`, `journal_verification.md`, `measurement/` (scripts + data measuring submission→acceptance times of 76 journals from PubMed/Crossref) |
| `manuscript/` | `Final_Manuscript.docx/.pdf`, `Supplementary_Material.docx/.pdf`, `cover_letter.docx/.pdf`, `EHRA_AI_checklist.docx/.pdf` (required for AI studies), `graphical_abstract.tiff/.png`; `source/` (text with data tokens), `build/` (builder: tokens → numbers from results; citations → verified Vancouver references; DOCX renderer; final audit), `refs/verified_references.json` |
| `code/` | Complete reproducible pipeline (`run_all.py --mode quick|full`, `src/`, `experiments/`, `scripts/`, `tests/`, `config/`, `requirements.txt`, `environment.yml`, `README.md`) |
| `results/` | `raw_results.csv` (per patient × estimator × detector × seed × cohort), `metrics.json`, `statistics.json`, `intervals.csv`, `window_metrics.csv`, robustness/revision/sensitivity outputs, `efficiency.json`, `leakage_audit.json`, `dataset_summary.json`, saved models, `experiment_logs/` |
| `figures/` | All figures (PNG + 300-dpi TIFF), generated from result files |
| `tables/` | All tables (CSV + Markdown), generated from result files |
| `supplementary/` | `S1_research_design_preregistration.md` (pre-registration + amendments), `S2_literature_matrix.md` |
| `REVIEW/` | `review_01.md` … `review_10.md` (ten independent review rounds with author responses), `final_audit.md`, `final_audit_checks.json`, `rejection_risk_report.md` |

**Before submission the authors must:** insert author names/affiliations/corresponding author, funding and conflict-of-interest statements, the public repository URL/DOI, confirm the AI-use disclosure, and personally verify the analyses (see `REVIEW/rejection_risk_report.md`).
