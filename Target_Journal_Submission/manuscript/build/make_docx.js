// Render build/manuscript.json to a Europace-formatted Word file.
// A4, 2.5 cm margins, double spacing, 12-pt Times New Roman, continuous line numbers, page numbers,
// order: title page, abstract + keywords, What's New, main text, declarations, references,
// tables (one per page), figure legends with alt text, figures (one per page).
const fs = require("fs");
const path = require("path");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Footer, PageNumber, Table, TableRow,
  TableCell, WidthType, ShadingType, ImageRun, PageBreak, LineNumberRestartFormat, BorderStyle, LevelFormat } = d;

const M = JSON.parse(fs.readFileSync(path.join(__dirname, process.argv[2] || "manuscript.json"), "utf8"));
const OUT = process.argv[3] || path.join(__dirname, "..", "Final_Manuscript.docx");
const FONT = "Times New Roman";
const DOUBLE = { line: 480 };

const tr = (r, size) => new TextRun({ text: r.text, bold: !!r.bold, italics: !!r.italic, superScript: !!r.sup,
  subScript: !!r.sub, font: FONT, size: size || 24 });
const para = (runs, opts = {}) => new Paragraph({ children: runs.map(r => tr(r, opts.size)), spacing: { ...DOUBLE, after: 0 },
  alignment: opts.align || AlignmentType.LEFT, keepNext: !!opts.keepNext, indent: opts.indent });
const text = (t, o = {}) => para([{ text: t, bold: o.bold, italic: o.italic }], o);
const pb = () => new Paragraph({ children: [new PageBreak()] });

const children = [];
// ---------- title page ----------
const T = M.title_page;
children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: T.title, bold: true, font: FONT, size: 28 })], spacing: { ...DOUBLE, after: 240 } }));
children.push(text(`Short title: ${T.running_title}`));
children.push(text(T.authors));
for (const a of T.affiliations) children.push(text(a));
children.push(text(""));
children.push(text("Corresponding author: " + T.corresponding));
children.push(text(`Word count (main text, excluding abstract, references, tables and figure legends): ${T.word_count}`));
children.push(text(`Article type: ${T.article_type}`));
children.push(pb());

// ---------- body ----------
for (const s of M.sections) {
  for (const b of s.blocks) {
    if (b.type === "pagebreak") { children.push(pb()); continue; }
    if (b.type === "heading") {
      children.push(new Paragraph({ heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][b.level - 1],
        children: b.runs.map(r => new TextRun({ text: r.text, bold: true, italics: b.level === 3, font: FONT, size: b.level === 1 ? 26 : 24 })),
        spacing: { ...DOUBLE, before: 240, after: 0 }, keepNext: true }));
      continue;
    }
    if (b.type === "bullet") { children.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, children: b.runs.map(r => tr(r)), spacing: { ...DOUBLE, after: 0 } })); continue; }
    children.push(para(b.runs));
  }
}
// ---------- references ----------
children.push(pb());
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "References", bold: true, font: FONT, size: 26 })], spacing: { ...DOUBLE, after: 0 } }));
for (const r of M.references) children.push(text(r));

// ---------- tables ----------
const PAGEW = 11906 - 2 * 1418; // A4 width minus 2.5 cm margins (DXA)
for (const t of M.tables) {
  children.push(pb());
  children.push(new Paragraph({ children: [new TextRun({ text: t.title, bold: true, font: FONT, size: 22 })], spacing: { line: 276, after: 120 }, keepNext: true }));
  const n = t.header.length;
  const first = Math.round(PAGEW * (n > 6 ? 0.22 : 0.28));
  const other = Math.floor((PAGEW - first) / Math.max(n - 1, 1));
  const widths = [first, ...Array(n - 1).fill(other)];
  const total = widths.reduce((a, b) => a + b, 0);
  const sz = n > 7 ? 14 : n > 5 ? 16 : 18;
  const cell = (txt, w, head) => new TableCell({ width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "E8E8E8" } : undefined,
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ children: [new TextRun({ text: String(txt), bold: head, font: FONT, size: sz })], spacing: { line: 240 } })] });
  const rows = [new TableRow({ tableHeader: true, children: t.header.map((h, i) => cell(h, widths[i], true)) })];
  for (const r of t.rows) rows.push(new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, widths[i], false)) }));
  children.push(new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows }));
  if (t.note) children.push(new Paragraph({ children: [new TextRun({ text: t.note, font: FONT, size: 18 })], spacing: { line: 276, before: 120 } }));
}
// ---------- figure legends ----------
children.push(pb());
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Figure legends", bold: true, font: FONT, size: 26 })], spacing: { ...DOUBLE, after: 0 } }));
for (const f of M.figures) {
  children.push(para([{ text: f.label + " ", bold: true }, ...f.legend]));
  children.push(para([{ text: "Alt text: ", italic: true }, { text: f.alt }]));
}
// ---------- figures ----------
const sizeOf = (p) => { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; };
for (const f of M.figures) {
  if (!fs.existsSync(f.file)) continue;
  children.push(pb());
  const { w, h } = sizeOf(f.file);
  const maxW = 600, maxH = 820;
  let W = maxW, H = Math.round(maxW * h / w); if (H > maxH) { H = maxH; W = Math.round(maxH * w / h); }
  children.push(new Paragraph({ children: [new TextRun({ text: f.label, bold: true, font: FONT, size: 22 })], keepNext: true }));
  children.push(new Paragraph({ children: [new ImageRun({ type: "png", data: fs.readFileSync(f.file), transformation: { width: W, height: H },
    altText: { title: f.label, description: f.alt, name: f.label } })] }));
}

const doc = new Document({
  creator: "Authors", title: T.title, description: "Manuscript submitted to EP Europace",
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONT, size: 28, bold: true }, paragraph: { spacing: { before: 0, after: 240 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true }, paragraph: { spacing: { before: 240, after: 0 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true }, paragraph: { spacing: { before: 240, after: 0 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, italics: true }, paragraph: { spacing: { before: 120, after: 0 }, keepNext: true, outlineLevel: 2 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, bottom: 1418, left: 1418, right: 1418 } },
      lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT); });
