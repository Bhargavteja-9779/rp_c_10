# Journal comparison (internal candidate evaluation)

Method: for every candidate, the median submission→acceptance time was **measured** from article-level metadata (PubMed `received`/`accepted` history dates or Crossref `received`/`accepted` assertions), for articles published since 2025-07-01 (or 2024-07-01 in the refined analysis), excluding reviews/editorials/letters in the refined analysis. Scripts: `measurement/`. Full table of all measured journals: `measurement/all_journals_table.md`.
JIF values were taken from publisher pages where fetched; otherwise marked "not verified" because Clarivate JCR could not be accessed directly.

## Shortlist (scientifically plausible venues for an ML/AF-burden study)

| Candidate | Publisher | JIF (verification) | Median days, all original research | Median days, ML/AI papers | Scope fit | Decision |
|---|---|---|---|---|---|---|
| **EP Europace** | OUP | 10.2 (OUP About page), rank 17/237 → Q1 | **65** (n=281) | **72.5** (n=38) | Arrhythmia/EP incl. AI & wearables | **SELECTED** |
| Heart Rhythm | Elsevier | not verified | 79 (n=330) | 81 (n=66) | Excellent | Rejected: exceeds 72 d |
| JACC: Clinical Electrophysiology | Elsevier | not verified | 91 | 119 | Excellent | Rejected: slow |
| European Heart Journal – Digital Health | OUP | not verified | 111 | 118 | Excellent | Rejected: slow (also not certain Q1) |
| European Heart Journal | OUP | not verified (very high) | 179 | 219 | Too high bar for public-data methods study | Rejected |
| International Journal of Cardiology | Elsevier | not verified | 86 | 91 | Good | Rejected: slow |
| Journal of Arrhythmia | Wiley | not verified | 89.5 | 116.5 | Good | Rejected: slow, lower JIF |
| Computers in Biology and Medicine | Elsevier | not verified | 124 | 168 | Good (methods) | Rejected: slow |
| IEEE JBHI / TBME / TNNLS | IEEE | not verified | no received/accepted metadata available | – | Good | Rejected: timeline unverifiable |
| Physiological Measurement | IOP | not verified | 127 | – | Excellent (methods) | Rejected: slow, lower JIF |
| Journal of Biomedical Informatics | Elsevier | not verified | 147 | – | Good | Rejected: slow |
| Int. J. Medical Informatics | Elsevier | not verified | 88.5 | 84 | Partial | Rejected: slow |
| npj Digital Medicine | Springer Nature | not verified | 136 | – | Good | Rejected: slow |
| Briefings in Bioinformatics / Bioinformatics / JAMIA / GigaScience | OUP | not verified | 120 / 152 / 121 / 196 | – | Poor (not cardiology) | Rejected |
| Analytica Chimica Acta | Elsevier | not verified | 61 | 84 | No fit (chemistry) | Rejected: scope |
| Virtual and Physical Prototyping | T&F | not verified | 66 | 64.5 | No fit (additive manufacturing) | Rejected: scope |
| Bioresource Technology | Elsevier | not verified | 76 | 63 | No fit | Rejected: scope |
| Research (SPJ) | AAAS/SPJ | not verified | 91.5 | – | Weak | Rejected: slow |
| Journal of King Saud Univ – CIS | Springer | not verified | 87 | – | Generic CS | Rejected: slow, scope |

## Constraints that could not be fully satisfied/verified
* **Acceptance ≤72 days cannot be guaranteed for any individual manuscript.** The measured median for Europace original research (65 d) is below the limit, but the AI-paper subgroup median (72.5 d) sits at the limit, and ~50 % of published AI papers took longer than 72 days. Rejected manuscripts are not observable in this measurement.
* The JCR quartile was inferred from the publisher-displayed category rank (17/237), not read from the JCR database itself.
* APC for research articles was not verifiable from the publisher's pages at the time of selection.
