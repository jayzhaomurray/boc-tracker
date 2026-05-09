"""
Generate project-evolution-2026-05-09.pdf from the markdown source
using reportlab Platypus (pure-Python, no GTK/pango dependencies).
"""
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable

base = Path(__file__).parent.parent
md_path = base / "analyses/project-evolution-2026-05-09.md"
pdf_path = base / "project-evolution-2026-05-09.pdf"

W, H = A4
styles = getSampleStyleSheet()

normal = ParagraphStyle(
    "body", parent=styles["Normal"],
    fontSize=10.5, leading=15, alignment=TA_JUSTIFY,
    spaceAfter=6, fontName="Times-Roman"
)
h1_style = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=17, leading=22, spaceAfter=6, spaceBefore=0,
    fontName="Times-Bold", textColor=colors.HexColor("#111111")
)
h2_style = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=12.5, leading=16, spaceBefore=16, spaceAfter=4,
    fontName="Times-Bold", textColor=colors.HexColor("#1a1a1a")
)
h3_style = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontSize=11, leading=14, spaceBefore=10, spaceAfter=3,
    fontName="Times-Bold", textColor=colors.HexColor("#222222")
)
cell_style = ParagraphStyle(
    "cell", parent=styles["Normal"],
    fontSize=9.5, leading=13, fontName="Times-Roman", alignment=TA_LEFT
)
cell_hdr = ParagraphStyle(
    "cell_hdr", parent=styles["Normal"],
    fontSize=9.5, leading=13, fontName="Times-Bold", alignment=TA_LEFT
)
bullet_style = ParagraphStyle(
    "bullet", parent=normal,
    leftIndent=14, spaceAfter=2
)

INLINE_RE = re.compile(r'\*\*(.+?)\*\*|\*(?!\*)(.+?)\*(?!\*)|`(.+?)`')


def md_inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    def repl(m):
        if m.group(1):
            return "<b>{}</b>".format(m.group(1))
        if m.group(2):
            return "<i>{}</i>".format(m.group(2))
        if m.group(3):
            return "<font name='Courier' size='9'>{}</font>".format(m.group(3))
    return INLINE_RE.sub(repl, text)


def build_table(rows):
    if not rows:
        return None
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    data = []
    for i, row in enumerate(rows):
        sty = cell_hdr if i == 0 else cell_style
        data.append([Paragraph(md_inline(c), sty) for c in row])
    col_width = (W - 5.2 * cm) / col_count
    t = Table(data, colWidths=[col_width] * col_count, repeatRows=1)
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ])
    t.setStyle(ts)
    return t


def parse_gfm_table(table_lines):
    rows = []
    for line in table_lines:
        if re.match(r"^\s*\|[-| :]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(A4[0] / 2, 1.4 * cm, str(doc.page))
    canvas.restoreState()


def md_to_story(md_text):
    story = []
    lines = md_text.splitlines()
    i = 0
    in_table = False
    table_lines = []
    h2_buffer = []

    def flush_h2():
        nonlocal h2_buffer
        if h2_buffer:
            story.append(KeepTogether(h2_buffer[:4]))
            story.extend(h2_buffer[4:])
            h2_buffer = []

    def emit(flowable):
        if h2_buffer:
            h2_buffer.append(flowable)
        else:
            story.append(flowable)

    while i < len(lines):
        line = lines[i]

        # Table detection
        if "|" in line and re.match(r"^\s*\|", line):
            if not in_table:
                flush_h2()
                in_table = True
                table_lines = []
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            tbl = build_table(parse_gfm_table(table_lines))
            if tbl:
                story.append(tbl)
                story.append(Spacer(1, 6))
            in_table = False
            table_lines = []
            # fall through to process current line

        # HR
        if re.match(r"^---+\s*$", line):
            flush_h2()
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#cccccc")))
            story.append(Spacer(1, 4))
            i += 1
            continue

        # H1
        m = re.match(r"^# (.+)", line)
        if m:
            flush_h2()
            story.append(Paragraph(md_inline(m.group(1)), h1_style))
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=colors.HexColor("#111111"), spaceAfter=8))
            i += 1
            continue

        # H2
        m = re.match(r"^## (.+)", line)
        if m:
            flush_h2()
            h2_buffer = [
                Spacer(1, 4),
                Paragraph(md_inline(m.group(1)), h2_style),
                HRFlowable(width="100%", thickness=0.5,
                            color=colors.HexColor("#cccccc"), spaceAfter=4),
            ]
            i += 1
            continue

        # H3
        m = re.match(r"^### (.+)", line)
        if m:
            emit(Paragraph(md_inline(m.group(1)), h3_style))
            i += 1
            continue

        # Blank
        if line.strip() == "":
            if h2_buffer:
                flush_h2()
            else:
                story.append(Spacer(1, 4))
            i += 1
            continue

        # Bullet
        m = re.match(r"^(\s*)[-*] (.+)", line)
        if m:
            indent = len(m.group(1))
            sty = ParagraphStyle(
                "b{}".format(indent), parent=bullet_style,
                leftIndent=14 + indent * 8
            )
            emit(Paragraph("&#8226; " + md_inline(m.group(2)), sty))
            i += 1
            continue

        # Ordered list
        m = re.match(r"^(\s*)\d+\. (.+)", line)
        if m:
            indent = len(m.group(1))
            sty = ParagraphStyle(
                "ob{}".format(indent), parent=bullet_style,
                leftIndent=14 + indent * 8
            )
            emit(Paragraph(md_inline(m.group(2)), sty))
            i += 1
            continue

        # Regular paragraph — accumulate until blank / heading / table
        para_lines = []
        while i < len(lines):
            ln = lines[i]
            if (ln.strip() == "" or re.match(r"^[#>]", ln) or
                    "|" in ln or re.match(r"^---", ln) or
                    re.match(r"^\s*[-*] ", ln) or re.match(r"^\s*\d+\. ", ln)):
                break
            para_lines.append(ln.strip())
            i += 1
        if para_lines:
            emit(Paragraph(md_inline(" ".join(para_lines)), normal))
        continue

    flush_h2()
    if in_table and table_lines:
        tbl = build_table(parse_gfm_table(table_lines))
        if tbl:
            story.append(tbl)
    return story


if __name__ == "__main__":
    md_text = md_path.read_text(encoding="utf-8")
    story = md_to_story(md_text)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.5 * cm,
        title="BoC Tracker: Project Evolution 2026-05-09",
        author="Jay Zhao-Murray",
    )
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    size_kb = pdf_path.stat().st_size // 1024
    print("PDF written OK:", pdf_path, "({} KB)".format(size_kb))
