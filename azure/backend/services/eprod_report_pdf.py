"""
EPROD AP Cycle Audit Report — PDF generator (reportlab).

Single entry point: generate_ap_cycle_audit_report(cycle, output_path).

The `cycle` dict shape (produced by backend/api/eprod_cycle.py::_run_pipeline):
  cycle_id, started_at, ended_at, duration_ms, trigger, source, doc_type,
  extracted, validation_findings, hitl, audit_trail[], status, agents[],
  vendor, total, references, write_back, report
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FOREST = colors.HexColor("#047857")
INK    = colors.HexColor("#0F172A")
MUTED  = colors.HexColor("#64748B")
SOFT   = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
DANGER = colors.HexColor("#B91C1C")
WARN   = colors.HexColor("#B45309")
GOOD   = colors.HexColor("#047857")


# ─────────────────────── styles ───────────────────────

def _styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title":     ParagraphStyle("title", parent=base["Title"],
                                     fontName="Helvetica-Bold", fontSize=22,
                                     leading=26, textColor=FOREST, spaceAfter=8),
        "subtitle":  ParagraphStyle("subtitle", parent=base["Normal"],
                                     fontName="Helvetica", fontSize=11,
                                     leading=14, textColor=MUTED, spaceAfter=18),
        "h1":        ParagraphStyle("h1", parent=base["Heading1"],
                                     fontName="Helvetica-Bold", fontSize=14,
                                     leading=18, textColor=FOREST,
                                     spaceBefore=14, spaceAfter=8),
        "h2":        ParagraphStyle("h2", parent=base["Heading2"],
                                     fontName="Helvetica-Bold", fontSize=11,
                                     leading=14, textColor=INK,
                                     spaceBefore=10, spaceAfter=4),
        "body":      ParagraphStyle("body", parent=base["BodyText"],
                                     fontName="Helvetica", fontSize=10,
                                     leading=14, textColor=INK, spaceAfter=4),
        "small":     ParagraphStyle("small", parent=base["BodyText"],
                                     fontName="Helvetica", fontSize=9,
                                     leading=12, textColor=MUTED),
        "label":     ParagraphStyle("label", parent=base["BodyText"],
                                     fontName="Helvetica-Bold", fontSize=9,
                                     leading=11, textColor=MUTED),
        "value":     ParagraphStyle("value", parent=base["BodyText"],
                                     fontName="Helvetica", fontSize=10,
                                     leading=13, textColor=INK),
        "footer":    ParagraphStyle("footer", parent=base["BodyText"],
                                     fontName="Helvetica-Oblique", fontSize=8,
                                     leading=10, textColor=MUTED,
                                     alignment=1),
    }


def _fmt_ts(ms: Optional[int]) -> str:
    if not ms:
        return "—"
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _fmt_money(v: Any) -> str:
    try:
        n = float(v)
        return f"${n:,.2f}"
    except Exception:
        return str(v or "—")


def _result_badge(status: str) -> str:
    s = (status or "").upper()
    if "REJECT" in s or "HALT" in s:
        return f'<font color="#B91C1C"><b>{s}</b></font>'
    if "HITL APPROVED" in s:
        return f'<font color="#B45309"><b>{s}</b></font>'
    return f'<font color="#047857"><b>{s or "PASS"}</b></font>'


# ─────────────────────── builders ───────────────────────

def _kv_table(rows: List[List[str]], col_widths=None) -> Table:
    if col_widths is None:
        col_widths = [1.7 * inch, 4.3 * inch]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",   (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",  (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR",  (1, 0), (1, -1), INK),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("LINEBELOW",  (0, 0), (-1, -1), 0.25, BORDER),
    ]))
    return t


def _findings_table(findings: List[Dict[str, Any]]) -> Table:
    headers = ["Rule", "Expected", "Actual", "Severity", "Action"]
    rows: List[List[str]] = [headers]
    sev_styles: List[tuple] = []
    if not findings:
        rows.append(["(no validation findings)", "—", "—", "—", "—"])
    else:
        for i, f in enumerate(findings, start=1):
            sev = (f.get("severity") or "info").lower()
            rows.append([
                str(f.get("rule") or "—"),
                str(f.get("expected") or "—"),
                str(f.get("actual") or "—"),
                sev.upper(),
                str(f.get("action") or f.get("recommendation") or "—"),
            ])
            color = {
                "critical": DANGER, "high": DANGER,
                "medium": WARN, "warn": WARN,
                "low": MUTED, "info": MUTED, "pass": GOOD,
            }.get(sev, INK)
            sev_styles.append(("TEXTCOLOR", (3, i), (3, i), color))
            sev_styles.append(("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"))

    t = Table(rows, colWidths=[1.6 * inch, 1.3 * inch, 1.3 * inch, 0.8 * inch, 1.5 * inch])
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), FOREST),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("ALIGN",      (3, 0), (3, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("GRID",       (0, 0), (-1, -1), 0.25, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
    ] + sev_styles
    t.setStyle(TableStyle(style))
    return t


def _audit_trail_table(trail: List[Dict[str, Any]]) -> Table:
    rows: List[List[str]] = [["Stage", "Started", "Duration", "Outcome"]]
    if not trail:
        rows.append(["(no audit entries)", "—", "—", "—"])
    else:
        for e in trail:
            rows.append([
                str(e.get("stage") or "—"),
                _fmt_ts(e.get("started_at")),
                f"{e.get('duration_ms', 0)} ms",
                str(e.get("outcome") or "ok"),
            ])
    t = Table(rows, colWidths=[1.4 * inch, 2.0 * inch, 1.0 * inch, 2.1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FOREST),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("GRID",       (0, 0), (-1, -1), 0.25, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
    ]))
    return t


def _extracted_two_col(extracted: Dict[str, Any]) -> Table:
    items: List[List[str]] = []
    skip = {"line_items"}
    for k, v in extracted.items():
        if k in skip:
            continue
        if isinstance(v, (list, dict)):
            v = f"{len(v)} entries" if isinstance(v, list) else "{…}"
        conf = extracted.get("_confidence", {}).get(k)
        conf_str = f"  ({conf:.0%})" if isinstance(conf, (int, float)) else ""
        items.append([str(k).replace("_", " ").title(), f"{v}{conf_str}"])

    # split into 2-col layout
    half = (len(items) + 1) // 2
    left = items[:half]
    right = items[half:]
    while len(right) < len(left):
        right.append(["", ""])

    rows = []
    for l, r in zip(left, right):
        rows.append([l[0], l[1], r[0], r[1]])

    t = Table(rows, colWidths=[1.4 * inch, 1.6 * inch, 1.4 * inch, 1.6 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",   (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR",  (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR",  (2, 0), (2, -1), MUTED),
        ("TEXTCOLOR",  (1, 0), (1, -1), INK),
        ("TEXTCOLOR",  (3, 0), (3, -1), INK),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("LINEBELOW",  (0, 0), (-1, -1), 0.25, BORDER),
    ]))
    return t


# ─────────────────────── main ───────────────────────

def generate_ap_cycle_audit_report(cycle: Dict[str, Any], output_path: Path) -> Path:
    """Generate the EPROD AP Cycle Audit Report PDF for one completed cycle."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    s = _styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=f"EPROD AP Cycle Audit Report — {cycle.get('cycle_id', '')}",
        author="Apex EPROD",
    )

    story: List[Any] = []

    # ── PAGE 1 · COVER + SUMMARY ──
    story.append(Paragraph("EPROD &middot; AP Cycle Audit Report", s["title"]))
    story.append(Paragraph(
        "Enterprise Products Operating LLC &middot; Midstream Accounts Payable "
        "&middot; Apex AI Platform",
        s["subtitle"],
    ))

    extracted = cycle.get("extracted", {}) or {}
    status = cycle.get("status") or "PASS"

    cover_rows = [
        ["Cycle ID",         str(cycle.get("cycle_id", "—"))],
        ["Generated",        _fmt_ts(cycle.get("ended_at"))],
        ["Document Type",    str(cycle.get("doc_type", "—")).replace("_", " ").title()],
        ["Source File",      str(cycle.get("source", "—"))],
        ["Trigger",          str(cycle.get("trigger", "—"))],
        ["Duration",         f"{cycle.get('duration_ms', 0)} ms"],
    ]
    story.append(_kv_table(cover_rows))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Result", s["h1"]))
    story.append(Paragraph(_result_badge(status), s["body"]))
    story.append(Spacer(1, 6))

    summary_rows = [
        ["Vendor",        str(extracted.get("vendor") or cycle.get("vendor") or "—")],
        ["Amount",        _fmt_money(extracted.get("total") or cycle.get("total"))],
        ["Asset Code",    str(extracted.get("asset_code") or "—")],
        ["PO Reference",  str(extracted.get("po_reference") or "—")],
        ["MSA Reference", str(extracted.get("msa_reference") or "—")],
        ["AFE Reference", str(extracted.get("afe_reference") or "—")],
    ]
    story.append(_kv_table(summary_rows))
    story.append(Spacer(1, 14))

    agents = cycle.get("agents") or []
    story.append(Paragraph("Apex Agents Involved", s["h2"]))
    story.append(Paragraph(", ".join(agents) if agents else "—", s["body"]))

    # ── PAGE 2 · EXTRACTION ──
    story.append(PageBreak())
    story.append(Paragraph("Extraction Summary", s["h1"]))
    story.append(Paragraph(
        "Fields recovered by Azure AI Document Intelligence, with per-field confidence scores. "
        "Fields below 0.90 are flagged for spot review in Audit Lens.",
        s["small"],
    ))
    story.append(Spacer(1, 10))
    if extracted:
        story.append(_extracted_two_col(extracted))
    else:
        story.append(Paragraph("(no extracted fields)", s["body"]))

    line_items = extracted.get("line_items") or []
    if line_items:
        story.append(Spacer(1, 14))
        story.append(Paragraph("Line Items", s["h2"]))
        li_rows: List[List[str]] = [["#", "Description", "Qty", "Unit", "Total"]]
        for i, li in enumerate(line_items, start=1):
            li_rows.append([
                str(i),
                str(li.get("description") or "—")[:60],
                str(li.get("quantity") or "—"),
                _fmt_money(li.get("unit_price") or li.get("unit")),
                _fmt_money(li.get("total") or li.get("amount")),
            ])
        t = Table(li_rows, colWidths=[0.3 * inch, 3.3 * inch, 0.6 * inch, 0.9 * inch, 0.9 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), FOREST),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
            ("GRID",       (0, 0), (-1, -1), 0.25, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)

    # ── PAGE 3 · VALIDATION ──
    story.append(PageBreak())
    story.append(Paragraph("Validation Findings", s["h1"]))
    story.append(Paragraph(
        "Per-rule results from the EPROD AP validation suite (MSA scope, tax codes, "
        "duplicate check, PO match, AFE balance, FERC tariff alignment).",
        s["small"],
    ))
    story.append(Spacer(1, 10))
    story.append(_findings_table(cycle.get("validation_findings") or []))

    # ── PAGE 4 · HITL DECISION + AUDIT TRAIL ──
    story.append(PageBreak())
    story.append(Paragraph("HITL Decision", s["h1"]))
    hitl = cycle.get("hitl") or {}
    if hitl:
        hitl_rows = [
            ["Request ID",  str(hitl.get("request_id") or "—")],
            ["Gate",        str(hitl.get("gate") or "—")],
            ["Severity",    str(hitl.get("severity") or "—").upper()],
            ["Reason",      str(hitl.get("reason") or "—")],
            ["Reviewer",    str(hitl.get("reviewer") or "—")],
            ["Decision",    str(hitl.get("decision") or "—").upper()],
            ["Decided At",  _fmt_ts(hitl.get("decided_at"))],
            ["Comment",     str(hitl.get("comment") or "—")],
        ]
        story.append(_kv_table(hitl_rows))
    else:
        story.append(Paragraph(
            "<b>Auto-approved within authority limits.</b> No HITL gate triggered for this cycle.",
            s["body"],
        ))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Audit Trail", s["h1"]))
    story.append(_audit_trail_table(cycle.get("audit_trail") or []))

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Audit Lens &middot; Immutable record &middot; 7-year retention &middot; "
        f"Event ID: AUDIT-{cycle.get('cycle_id','')}",
        s["footer"],
    ))

    doc.build(story)
    return output_path
