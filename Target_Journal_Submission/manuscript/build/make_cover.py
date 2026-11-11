"""Resolve data tokens in the cover letter and render it to DOCX (via make_simple_docx.js)."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuscript as B
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(os.path.dirname(HERE), "source")
tp = json.load(open(os.path.join(SRC, "title_page.json"))); B.CONST["title"] = tp["title"]
txt = B.resolve(open(os.path.join(SRC, "cover_letter.md")).read())
paras = []
for p in re.split(r"\n\s*\n", txt.strip()):
    p = " ".join(l.strip() for l in p.splitlines())
    p = p.replace("**", "")
    p = re.sub(r"\*([^*]+)\*", r"\1", p)
    paras.append({"text": p})
doc = {"title": "Cover letter", "paragraphs": paras, "font_size": 22}
json.dump(doc, open(os.path.join(HERE, "cover_letter.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(os.path.dirname(HERE), "cover_letter.md"), "w").write(txt)
subprocess.run(["node", os.path.join(HERE, "make_simple_docx.js"), os.path.join(HERE, "cover_letter.json"), os.path.join(os.path.dirname(HERE), "cover_letter.docx")], check=True)
