"""Measure submission->acceptance times from article-level metadata.
Sources: Crossref 'assertion' received/accepted (Springer, T&F, ...) and PubMed history dates."""
import json, sys, time, statistics, urllib.request, urllib.parse, re, xml.etree.ElementTree as ET
from datetime import date, datetime
UA = {"User-Agent": "acc-time-research-script/0.1"}
def get(url, tries=4):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 ** t)
    return None
def pdate(s):
    for f in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(s.strip(), f).date()
        except Exception: pass
    return None
def crossref(issn, n=300, frm="2025-07-01"):
    out, cursor = [], "*"
    while len(out) < n:
        q = f"https://api.crossref.org/journals/{issn}/works?rows=200&cursor={urllib.parse.quote(cursor)}&filter=from-pub-date:{frm},type:journal-article&select=DOI,assertion"
        b = get(q)
        if not b: break
        m = json.loads(b)["message"]; items = m["items"]
        if not items: break
        for i in items:
            a = {x.get("name"): x.get("value") for x in i.get("assertion", [])}
            if "received" in a and "accepted" in a:
                r, c = pdate(a["received"]), pdate(a["accepted"])
                if r and c and c >= r: out.append((c - r).days)
        cursor = m.get("next-cursor")
        if not cursor or len(items) < 200: break
    return out
def pubmed(jour, n=300, frm="2025/07/01"):
    term = f'"{jour}"[jour] AND ("{frm}"[dp] : "3000"[dp]) AND journal article[pt]'
    b = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=%d&term=%s" % (n, urllib.parse.quote(term)))
    ids = re.findall(rb"<Id>(\d+)</Id>", b or b"")
    out = []
    for k in range(0, len(ids), 150):
        x = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(i.decode() for i in ids[k:k+150]))
        time.sleep(0.4)
        if not x: continue
        for art in ET.fromstring(x).iter("PubmedArticle"):
            d = {}
            for p in art.iter("PubMedPubDate"):
                st = p.get("PubStatus")
                try: d[st] = date(int(p.findtext("Year")), int(p.findtext("Month")), int(p.findtext("Day")))
                except Exception: pass
            if "received" in d and "accepted" in d and d["accepted"] >= d["received"]:
                out.append((d["accepted"] - d["received"]).days)
    return out
def summ(v):
    if len(v) < 15: return {"n": len(v)}
    v = sorted(v); q = statistics.quantiles(v, n=4)
    return {"n": len(v), "median": statistics.median(v), "q1": q[0], "q3": q[2], "pct_le_72": round(100*sum(x <= 72 for x in v)/len(v), 1)}
if __name__ == "__main__":
    cands = json.load(open(sys.argv[1]))
    res = {}
    for c in cands:
        v = crossref(c["issn"]) if c.get("src") == "crossref" else pubmed(c["pm"])
        res[c["name"]] = {**c, **summ(v)}
        print(json.dumps(res[c["name"]]), flush=True)
    json.dump(res, open(sys.argv[2], "w"), indent=1)
