import sys, re, time, json, statistics, urllib.parse, xml.etree.ElementTree as ET
from datetime import date
sys.path.insert(0,'.')
from acc_times import get, crossref
EXC={"Review","Editorial","Comment","Letter","Practice Guideline","Guideline","Consensus Development Conference","Systematic Review","Meta-Analysis","Published Erratum","Case Reports"}
def pm(jour, extra="", n=400, frm="2024/07/01"):
    term=f'"{jour}"[jour] AND ("{frm}"[dp]:"3000"[dp]) {extra}'
    b=get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=%d&term=%s"%(n,urllib.parse.quote(term)))
    ids=[i.decode() for i in re.findall(rb"<Id>(\d+)</Id>",b or b"")]
    out=[]
    for k in range(0,len(ids),150):
        x=get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(ids[k:k+150])); time.sleep(0.4)
        for a in ET.fromstring(x).iter("PubmedArticle"):
            pts={p.text for p in a.iter("PublicationType")}
            if pts & EXC: continue
            d={}
            for p in a.iter("PubMedPubDate"):
                try: d[p.get("PubStatus")]=date(int(p.findtext("Year")),int(p.findtext("Month")),int(p.findtext("Day")))
                except: pass
            if "received" in d and "accepted" in d and d["accepted"]>=d["received"]:
                out.append(((d["accepted"]-d["received"]).days, a.findtext(".//ArticleTitle")))
    return out
def s(v):
    v=sorted(x[0] for x in v)
    if len(v)<8: return f"n={len(v)} {v}"
    q=statistics.quantiles(v,n=4); return f"n={len(v)} median={statistics.median(v)} IQR=({q[0]},{q[2]}) <=72d={100*sum(x<=72 for x in v)/len(v):.0f}%"
ML='AND ("machine learning"[tiab] OR "deep learning"[tiab] OR "neural network"[tiab] OR "artificial intelligence"[tiab])'
if __name__=="__main__":
 for j in ["Europace","Anal Chim Acta","Talanta","Spectrochim Acta A Mol Biomol Spectrosc","Bioresour Technol","Biosens Bioelectron","Int J Med Inform","Comput Biol Med","Water Res"]:
    a=pm(j); m=pm(j,ML,frm="2023/01/01")
    print(f"{j:42s} original-research: {s(a)}\n{'':42s} ML-papers(2023+): {s(m)}",flush=True)
    if j=="Europace":
        for t in m[:40]: print("   ",t[0],(t[1] or "")[:110])
