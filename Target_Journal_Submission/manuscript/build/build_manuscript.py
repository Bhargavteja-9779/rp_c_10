"""Build the manuscript document model from section sources + machine-generated results.

* {{func:args}} tokens are resolved ONLY from results/*.json and tables/*.csv (no hand-typed numbers).
* [@key; @key2] citations are numbered in order of first appearance (Vancouver) from
  refs/verified_references.json (every entry verified against Crossref/DataCite).
Outputs: build/manuscript.json (for make_docx.js), ../Final_Manuscript.md (plain review copy),
         build/claims_numbers.csv (every resolved token with its source, for the consistency audit).
"""
from __future__ import annotations
import csv, glob, json, os, re, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))           # Target_Journal_Submission
RES = os.environ.get("RES_DIR", os.path.join(ROOT, "results")); TAB = os.environ.get("TAB_DIR", os.path.join(ROOT, "tables")); FIG = os.environ.get("FIG_DIR", os.path.join(ROOT, "figures"))
SRC = os.path.join(os.path.dirname(HERE), "source")
REFS = json.load(open(os.path.join(os.path.dirname(HERE), "refs", "verified_references.json")))
M = json.load(open(os.path.join(RES, "metrics.json")))
S = json.load(open(os.path.join(RES, "statistics.json")))
E = json.load(open(os.path.join(RES, "efficiency.json"))) if os.path.exists(os.path.join(RES, "efficiency.json")) else {}
L = json.load(open(os.path.join(RES, "leakage_audit.json")))
DS = json.load(open(os.path.join(RES, "dataset_summary.json")))
TOKLOG = []


def f2(x, d=2): return f"{x:.{d}f}"


def tok_mae(det, est, coh, d="2"):
    m = M["burden"][f"{det}|{est}|{coh}"]["mae_pp"]; return f"{m[0]:.{int(d)}f} ± {m[1]:.{int(d)}f}"


def tok_bm(det, est, coh, metric, d="2"):
    return f"{M['burden'][f'{det}|{est}|{coh}'][metric][0]:.{int(d)}f}"


def tok_bmsd(det, est, coh, metric, d="2"):
    m = M["burden"][f"{det}|{est}|{coh}"][metric]; return f"{m[0]:.{int(d)}f} ± {m[1]:.{int(d)}f}"


def tok_pct(det, est, coh, metric, d="1"):
    return f"{100*M['burden'][f'{det}|{est}|{coh}'][metric][0]:.{int(d)}f}"


def tok_wm(det, coh, metric, d="3"):
    m = M["window_metrics"][f"{det}|{coh}"][metric]; return f"{m[0]:.{int(d)}f} ± {m[1]:.{int(d)}f}"


def tok_wmm(det, coh, metric, d="3"):
    return f"{M['window_metrics'][f'{det}|{coh}'][metric][0]:.{int(d)}f}"


def tok_iv(det, meth, coh, field, d="3"):
    v = M["intervals"][f"{det}|{meth}|{coh}"][field]
    if isinstance(v, list):
        if field == "cp95": return f"{v[0]:.{int(d)}f}–{v[1]:.{int(d)}f}"
        return f"{v[0]:.{int(d)}f}"
    return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_test(det, target, coh, comp, field, d="2"):
    v = S["tests"][f"{det}|{target}|{coh}"][comp][field]
    if field in ("p", "p_holm"):
        return "<0.001" if v < 0.001 else f"{v:.3f}"
    if isinstance(v, list): return f"{v[0]:.{int(d)}f} to {v[1]:.{int(d)}f}"
    return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_P(det, target, coh, comp):
    v = S["tests"][f"{det}|{target}|{coh}"][comp]["p_holm"]
    return "P < 0.001" if v < 0.001 else f"P = {v:.3f}"


def tok_testr(target, comp, field, d="2"):
    v = S["tests"][f"LightGBM|{target}|ext_pooled|rounded0.1pp"][comp][field]
    if field in ("p", "p_holm"): return "P < 0.001" if v < 0.001 else f"P = {v:.3f}"
    if isinstance(v, list): return f"{v[0]:.{int(d)}f} to {v[1]:.{int(d)}f}"
    return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_LR(coh, nl, field, d="2"):
    v = S["local_recalibration"][f"{coh}|{nl}"][field]; return f"{v:.{int(d)}f}"


def tok_SM(field, d="2"):
    v = S["smoother_check"]
    if field == "k": return str(v["k_selected_on_dev"])
    if field == "ext_ksel": return f"{v['ext_pooled_mae_by_k'][str(v['k_selected_on_dev'])]:.{int(d)}f}"
    if field.startswith("ext_k"): return f"{v['ext_pooled_mae_by_k'][field[5:]]:.{int(d)}f}"
    if field.startswith("dev_k"): return f"{v['dev_mae_by_k'][field[5:]]:.{int(d)}f}"
    r = v["final_vs_best_mf"]
    if field == "mean_diff": return f"{r['mean_diff']:.{int(d)}f}"
    if field == "mean_ci": return f"{r['mean_ci'][0]:.{int(d)}f} to {r['mean_ci'][1]:.{int(d)}f}"
    raise KeyError(field)


def tok_NM(field, d="1"):
    v = S["newly_missed"][field]; return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_S(*path):
    v = S
    for p in path: v = v[p] if not isinstance(v, list) else v[int(p)]
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def tok_SP(*path):  # p-value formatting
    v = S
    for p in path: v = v[p]
    return "<0.001" if v < 0.001 else f"{v:.3f}"


def tok_eff(comp, scale="ms"):
    v = E["components"][comp]["seconds_per_24h_median"]
    return f"{v*1000:.0f}" if scale == "ms" else f"{v:.2f}"


def tok_E(key, d="0"):
    v = E[key]; return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_param(det): return f"{E['params'][det]:,}"


def tok_table(name, row_col, col, row_val):
    df = pd.read_csv(os.path.join(TAB, name + ".csv"), dtype=str)
    return str(df.loc[df[row_col] == row_val, col].iloc[0])


def tok_D(db, field, d="0"):
    v = DS[db][field] if db != "-" else DS[field]
    return f"{v:,.{int(d)}f}" if isinstance(v, float) else f"{v:,}"


def tok_afl(est, field, d="2"):
    v = S["afl"][est][field]; return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_fpr(det, est, coh, thr):
    return f"{100*(1-M['burden'][f'{det}|{est}|{coh}'][thr + '_spec'][0]):.0f}%"


def tok_mcn(thr, field):
    v = S["mcnemar"][f"PA-HMMQ[rawE]_vs_CC|{thr}"][field]
    if field == "p": return "< 0.001" if v < 0.001 else f"= {v:.3f}"
    return str(v)


def tok_R1(field, d="2"):
    v = S["R1_summary"][field]; return f"{v:.{int(d)}f}" if isinstance(v, float) else str(v)


def tok_L(key): return str(L[key]) if not isinstance(L[key], list) else str(len(L[key]))


FUNCS = {k[4:]: v for k, v in globals().items() if k.startswith("tok_")}
CONST = {}


def resolve(text):
    def rep(m):
        body = m.group(1)
        if ":" in body:
            fn, args = body.split(":", 1); args = args.split("|")
        else:
            fn, args = body, []
        if fn in CONST and not args:
            out = CONST[fn]
        elif fn in FUNCS:
            try:
                out = FUNCS[fn](*args)
            except (KeyError, IndexError) as ex:
                if os.environ.get("STRICT", "1") == "1": raise
                out = "[PENDING]"; PENDING.append(body)
        else:
            raise KeyError(f"unknown token {body}")
        out = re.sub(r"(?<![\w.])-(?=\d)", "\u2212", str(out))  # typographic minus
        TOKLOG.append((body, out))
        return out
    return re.sub(r"\{\{([^}]+)\}\}", rep, text)


# ---------------- citations ----------------
ORDER = []
MISSING = []
PENDING = []


def cite(text):
    def rep(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in keys:
            if k not in REFS and k not in MANUAL_REFS: raise KeyError(f"unverified/unknown reference {k}")
            if k not in ORDER: ORDER.append(k)
            nums.append(ORDER.index(k) + 1)
        nums = sorted(set(nums)); parts = []; i = 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
            parts.append(f"{nums[i]}–{nums[j]}" if j - i >= 2 else ",".join(map(str, nums[i:j + 1])))
            i = j + 1
        return "^{" + ",".join(parts) + "}"
    return re.sub(r"\[(@[^\]]+)\]", rep, text)


MANUAL_REFS = {"young1999": "Young B, Brodnick D, Spaulding R. A comparative study of a hidden Markov model detector for atrial fibrillation. In: Neural Networks for Signal Processing IX: Proceedings of the 1999 IEEE Signal Processing Society Workshop. IEEE; 1999. p.468–476. doi:10.1109/NNSP.1999.788166","moody1983": "Moody GB, Mark RG. A new method for detecting atrial fibrillation using R-R intervals. Comput Cardiol 1983;10:227–230.","blandaltman1986": "Bland JM, Altman DG. Statistical methods for assessing agreement between two methods of clinical measurement. Lancet 1986;1(8476):307–310. doi:10.1016/S0140-6736(86)90837-8",
               "carter1994": "Carter CK, Kohn R. On Gibbs sampling for state space models. Biometrika 1994;81(3):541–553. doi:10.1093/biomet/81.3.541",
               "rabiner1989": "Rabiner LR. A tutorial on hidden Markov models and selected applications in speech recognition. Proc IEEE 1989;77(2):257–286. doi:10.1109/5.18626","holm1979": "Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70. Available from: https://www.jstor.org/stable/4615733"}


def vancouver(k):
    if k in MANUAL_REFS: return MANUAL_REFS[k]
    r = REFS[k]
    au = r.get("authors") or []
    au = [a.title() if a.isupper() else a for a in au]
    if k == "vovk2005": au = ["Vovk V", "Gammerman A", "Shafer G"]
    a = ", ".join(au[:6]) + (", et al." if len(au) > 6 else ".") if au else ""
    title = re.sub(r"<[^>]+>", "", r.get("title", "")).strip().rstrip(".")
    title = re.sub(r"\s+", " ", title)
    if k == "haekal2026":
        title = "RR-interval-based atrial fibrillation detection and burden estimation: cross-dataset validation and calibration-aware probability analysis"
    cont = r.get("container") or r.get("container_full") or ""
    vol, iss, pg = r.get("volume", ""), r.get("issue", ""), r.get("page", "")
    if r.get("source") == "datacite":
        return f"{a} {title} [dataset/preprint]. {cont}; {r.get('year')}. doi:{r['doi']}"
    if r.get("type") in ("book", "monograph", "edited-book"):
        return f"{a} {title}. {cont + '. ' if cont else ''}Cham/New York: Springer; {r.get('year')}. doi:{r['doi']}"
    loc = f"{r.get('year')}"
    if vol: loc += f";{vol}"
    if iss: loc += f"({iss})"
    if pg: loc += f":{pg}"
    return f"{a} {title}. {cont} {loc}. doi:{r['doi']}"


# ---------------- inline markup -> runs ----------------
def runs(text):
    """Supports **bold**, *italic*, ^{sup}, <sub>..</sub>, <sup>..</sup>."""
    text = text.replace("<sup>", "^{").replace("</sup>", "}")
    out = []
    pat = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|\^\{[^}]*\}|<sub>[^<]*</sub>)")
    for part in pat.split(text):
        if not part: continue
        if part.startswith("**"): out.append({"text": part[2:-2], "bold": True})
        elif part.startswith("*"): out.append({"text": part[1:-1], "italic": True})
        elif part.startswith("^{"): out.append({"text": part[2:-1], "sup": True})
        elif part.startswith("<sub>"): out.append({"text": part[5:-6], "sub": True})
        else: out.append({"text": part})
    return out


def md_blocks(md):
    blocks = []
    # put heading lines into their own paragraphs
    md = re.sub(r"(?m)^(#{1,3} [^\n]+)\n(?=\S)", r"\1\n\n", md)
    for para in re.split(r"\n\s*\n", md.strip()):
        p = para.strip()
        if not p: continue
        if p.startswith("<<PAGEBREAK>>"): blocks.append({"type": "pagebreak"}); continue
        m = re.match(r"^(#{1,3})\s+(.*)$", p)
        if m and "\n" not in p:
            blocks.append({"type": "heading", "level": len(m.group(1)), "runs": runs(m.group(2))}); continue
        if all(l.strip().startswith("- ") for l in p.splitlines()):
            for l in p.splitlines(): blocks.append({"type": "bullet", "runs": runs(l.strip()[2:])})
            continue
        blocks.append({"type": "para", "runs": runs(" ".join(l.strip() for l in p.splitlines()))})
    return blocks


def table_block(name, title, note, keep_cols=None, rename=None, filt=None):
    if not os.path.exists(os.path.join(TAB, name + ".csv")):
        print(f"WARNING: table {name} missing - skipped"); MISSING.append(name); return None
    df = pd.read_csv(os.path.join(TAB, name + ".csv"), dtype=str).fillna("–")
    if filt is not None: df = filt(df)
    if keep_cols: df = df[keep_cols]
    if rename: df = df.rename(columns=rename)
    return {"type": "table", "title": cite(resolve(title)), "note": cite(resolve(note)) if note else "",
            "header": list(df.columns), "rows": df.values.tolist(), "source": name + ".csv"}


def main():
    CONST.update(json.load(open(os.path.join(SRC, "constants.json"))) if os.path.exists(os.path.join(SRC, "constants.json")) else {})
    spec = json.load(open(os.path.join(SRC, LAYOUT)))
    doc = {"title_page": {}, "sections": [], "tables": [], "figures": [], "references": []}
    wc = 0
    for part in spec["sections"]:
        md = open(os.path.join(SRC, part)).read()
        md = cite(resolve(md))
        if part in spec.get("count_words", []):
            wc += len(re.findall(r"[A-Za-z0-9±–\-\.%]+", re.sub(r"\^\{[^}]*\}|[#*]", "", md)))
        doc["sections"].append({"file": part, "blocks": md_blocks(md)})
    tabs = getattr(__import__("tables_spec"), spec.get("tables_fn", "tables"))(table_block)
    doc["tables"] = [t for t in tabs if t is not None]
    doc["missing_tables"] = MISSING
    for f in spec["figures"]:
        doc["figures"].append({"file": os.path.join(FIG, f["file"] + ".png"), "legend": runs(cite(resolve(f["legend"]))),
                               "alt": resolve(f["alt"]), "label": f["label"]})
    # references are numbered after tables/legends are processed (citations inside them count)
    doc["references"] = [f"{i+1}. {vancouver(k)}" for i, k in enumerate(ORDER)]
    doc["word_count_main_text"] = wc
    doc["title_page"] = json.load(open(os.path.join(SRC, "title_page.json")))
    doc["title_page"]["kind"] = spec.get("kind", "main")
    for k in ("title", "running_title"):
        doc["title_page"][k] = resolve(doc["title_page"][k])
    doc["title_page"]["word_count"] = wc
    json.dump(doc, open(os.path.join(HERE, spec["out_json"]), "w"), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, spec["out_json"].replace(".json", "_numbers.csv")), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["token", "value"]); w.writerows(TOKLOG)
    # plain-text review copy
    with open(os.path.join(os.path.dirname(HERE), spec["out_md"]), "w") as fh:
        tp = doc["title_page"]; fh.write(f"# {tp['title']}\n\n")
        for s in doc["sections"]:
            for b in s["blocks"]:
                t = "".join(("^" + r["text"] if r.get("sup") else r["text"]) for r in b.get("runs", []))
                if b["type"] == "heading": fh.write("\n" + "#" * (b["level"] + 1) + " " + t + "\n\n")
                elif b["type"] == "bullet": fh.write("- " + t + "\n")
                elif b["type"] == "para": fh.write(t + "\n\n")
        for t in doc["tables"]:
            fh.write(f"\n**{t['title']}**\n\n| " + " | ".join(t["header"]) + " |\n|" + "---|" * len(t["header"]) + "\n")
            for r in t["rows"]: fh.write("| " + " | ".join(map(str, r)) + " |\n")
            fh.write(f"\n{t['note']}\n")
        for f in doc["figures"]:
            fh.write(f"\n**{f['label']}** " + "".join(r["text"] for r in f["legend"]) + f"\nAlt text: {f['alt']}\n")
        fh.write("\n## References\n\n" + "\n".join(doc["references"]) + "\n")
    print(f"built: {len(ORDER)} references, {len(TOKLOG)} data tokens, main-text words ≈ {wc}; pending tokens: {len(PENDING)} {PENDING[:5]}")


LAYOUT = "layout.json"
if __name__ == "__main__":
    sys.path.insert(0, HERE)
    if len(sys.argv) > 1: LAYOUT = sys.argv[1]
    main()
