"""Final consistency audit (Phase 34/35). Writes REVIEW/final_audit_checks.json and prints a summary.
Checks: strict build (no pending tokens), every citation verified, every figure/table file exists, guideline limits,
hand-typed numbers in sources (listed for manual review), claim checks against result files."""
import json, os, re, subprocess, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(os.path.dirname(HERE), "source")
out = {}
r = subprocess.run([sys.executable, "build_manuscript.py"], cwd=HERE, capture_output=True, text=True, env={**os.environ, "STRICT": "1"})
out["strict_build_main"] = r.returncode == 0; out["build_main_msg"] = (r.stdout + r.stderr).strip().splitlines()[-1:]
r2 = subprocess.run([sys.executable, "build_manuscript.py", "layout_supp.json"], cwd=HERE, capture_output=True, text=True, env={**os.environ, "STRICT": "1"})
out["strict_build_supp"] = r2.returncode == 0; out["build_supp_msg"] = (r2.stdout + r2.stderr).strip().splitlines()[-2:]
M = json.load(open(os.path.join(HERE, "manuscript.json"))); Sp = json.load(open(os.path.join(HERE, "supplement.json")))
out["word_count_main_text"] = M["word_count_main_text"]; out["word_limit_ok"] = M["word_count_main_text"] <= 5000
out["n_references"] = len(M["references"]); out["ref_limit_ok"] = len(M["references"]) <= 100
wn = open(os.path.join(SRC, "01_whatsnew.md")).read()
out["whats_new_words_approx"] = len(re.sub(r"\{\{[^}]+\}\}", "X", wn).split()); out["whats_new_bullets"] = wn.count("\n- ")
out["keywords"] = len(open(os.path.join(SRC, "00_abstract.md")).read().split("**Keywords**")[1].split("•"))
out["missing_figures"] = [f["file"] for f in M["figures"] + Sp["figures"] if not os.path.exists(f["file"])]
out["missing_tables"] = M.get("missing_tables", []) + Sp.get("missing_tables", [])
out["figures_with_alt_text"] = all(f.get("alt") for f in M["figures"] + Sp["figures"])
# references verified
refs = json.load(open(os.path.join(os.path.dirname(HERE), "refs", "verified_references.json")))
cited = set(re.findall(r"@([a-z_0-9]+)", "".join(open(os.path.join(SRC, f)).read() for f in os.listdir(SRC) if f.endswith(".md"))))
manual = {"holm1979", "moody1983", "young1999"}
out["unverified_citations"] = sorted(k for k in cited if k not in refs and k not in manual)
# hand-typed numbers in source text outside tokens (for manual review)
nums = {}
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".md") or f.startswith("cover"): continue
    t = re.sub(r"\{\{[^}]+\}\}", "", open(os.path.join(SRC, f)).read()); t = re.sub(r"\[@[^\]]+\]", "", t)
    nums[f] = sorted(set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?%?", t)))
out["hand_typed_numbers_for_review"] = nums
# every supplementary table/figure cited in the main text
main_txt = "".join(open(os.path.join(SRC, f)).read() for f in json.load(open(os.path.join(SRC, "layout.json")))["sections"])
cited_t = set(); cited_f = set()
for m in re.finditer(r"Supplementary Tables? (S\d+)(?:[–-](S\d+))?((?:, S\d+)*)", main_txt):
    a = int(m.group(1)[1:]); b = int(m.group(2)[1:]) if m.group(2) else a
    cited_t.update(range(a, b + 1)); cited_t.update(int(x) for x in re.findall(r"S(\d+)", m.group(3) or ""))
for m in re.finditer(r"Supplementary Figures? (S\d+)(?:[–-](S\d+))?", main_txt):
    a = int(m.group(1)[1:]); b = int(m.group(2)[1:]) if m.group(2) else a; cited_f.update(range(a, b + 1))
supp_t = sorted(int(re.match(r"Table S(\d+)", t["title"]).group(1)) for t in Sp["tables"])
supp_f = sorted(int(f["label"].split("S")[1]) for f in Sp["figures"])
out["supp_tables_not_cited_in_main"] = [t for t in supp_t if t not in cited_t]
out["supp_tables_cited_but_missing"] = sorted(t for t in cited_t if t not in supp_t)
out["supp_figures_not_cited_in_main"] = [x for x in supp_f if x not in cited_f]
out["supp_figures_cited_but_missing"] = sorted(x for x in cited_f if x not in supp_f)
# claim checks
R = pd.read_csv(os.path.join(ROOT, "results", "raw_results.csv")); R["ae"] = (R.estimate - R.true_burden).abs()
x = R[R.cohort.str.startswith("ext_") & R.estimator.isin(["CC", "PA-HMMQ[rawE]"])].groupby(["detector", "cohort", "estimator"]).ae.mean().unstack()
out["claim_final_beats_CC_all_9_combinations"] = bool((x["PA-HMMQ[rawE]"] < x["CC"]).all())
tm = pd.read_csv(os.path.join(ROOT, "tables", "table3_burden_mae_LightGBM.csv"), dtype=str)
mins = {}
for c in ["ext_shdb-af", "ext_cpsc2021", "ext_icentia11k", "ext_pooled"]:
    v = tm.set_index("Estimator")[c].str.split(" ± ").str[0].astype(float)
    v = v[[i for i in v.index if "R1" not in i]]
    mins[c] = v.idxmin()
out["claim_final_lowest_mae_each_external_cohort_LightGBM"] = mins
d = pd.read_csv(os.path.join(ROOT, "tables", "table11_sensitivity_trainfrac_window.csv"), dtype=str)
ok = True
for s_, g in d.groupby("Setting"):
    for c in ["ext_shdb-af", "ext_cpsc2021"]:
        v = g.set_index("Estimator")[c].str.split(" ± ").str[0].astype(float); ok &= v.idxmin() == "PA-HMMQ[rawE]"
out["claim_final_lowest_in_all_sensitivity_settings"] = bool(ok)
p = os.path.join(ROOT, "tables", "table12_robustness.csv")
if os.path.exists(p):
    rb = pd.read_csv(p, dtype=str); res = {}
    for (det, cond), g in rb.groupby(["Detector", "Condition"]):
        v = g.iloc[0][[c for c in g.columns if c not in ("Detector", "Condition")]].str.split(" ± ").str[0].astype(float)
        res[f"{det}|{cond}"] = v.idxmin()
    out["robustness_best_estimator_by_condition"] = res
json.dump(out, open(os.path.join(ROOT, "REVIEW", "final_audit_checks.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "hand_typed_numbers_for_review"}, indent=1))
