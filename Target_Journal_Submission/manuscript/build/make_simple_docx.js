// Generic simple document: {title, paragraphs:[string|{text,bold}], tables:[{caption, header, rows, widths?}], font_size?}
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, Footer, PageNumber } = require("docx");
const J = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const FONT = "Times New Roman", SZ = J.font_size || 22;
const P = (t, o = {}) => new Paragraph({ spacing: { after: 120, line: o.line || 300 }, alignment: o.align, children: [new TextRun({ text: t, bold: !!o.bold, font: FONT, size: o.size || SZ })] });
const kids = [new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: J.title, bold: true, font: FONT, size: 28 })] })];
for (const p of J.paragraphs || []) kids.push(typeof p === "string" ? P(p) : P(p.text, p));
const W = 11906 - 2 * 1134;
for (const t of J.tables || []) {
  if (t.caption) kids.push(P(t.caption, { bold: true }));
  const n = t.header.length; const widths = t.widths || Array(n).fill(Math.floor(W / n));
  const cell = (x, w, h) => new TableCell({ width: { size: w, type: WidthType.DXA }, shading: h ? { type: ShadingType.CLEAR, color: "auto", fill: "E8E8E8" } : undefined,
    margins: { top: 40, bottom: 40, left: 60, right: 60 }, children: [new Paragraph({ children: [new TextRun({ text: String(x), bold: h, font: FONT, size: 18 })] })] });
  kids.push(new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: t.header.map((h, i) => cell(h, widths[i], true)) }), ...t.rows.map(r => new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, widths[i], false)) }))] }));
  kids.push(P(""));
}
const doc = new Document({ styles: { default: { document: { run: { font: FONT, size: SZ } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children: kids }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[3], b); console.log("wrote", process.argv[3]); });
