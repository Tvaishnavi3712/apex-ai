"""
Hero PDF generator — produces the 3 PDFs the demo's hero scenario actually
clicks on, formatted to look like real STP documents (header block,
revision/date/owner, content body, signature block).

Output (all written to synthetic-data/nuclear_operations/pdfs/):

  • STP-415_business_travel.pdf       (UC-1 cited PDF, $75 meal allowance)
  • WO-2026-00871_work_package.pdf    (UC-2 cited PDF, P-3A PM-7B work package)
  • 0PMP-RCS-7B_procedure.pdf         (UC-2/UC-4 cited PDF, RCP bearing PM)

These PDFs are deliberately MORE compact and well-formed than scanned WPs —
they're meant to render cleanly when an STP exec clicks the citation link
mid-demo. The "scanned-style" 80+ work-package PDFs from the original spec
remain deferred (no real-time use during the demo).

Usage:
    python3 generate_hero_pdfs.py            # write all 3
    python3 generate_hero_pdfs.py --force    # overwrite existing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


OUT_DIR = Path(__file__).resolve().parent / "pdfs"
OUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

STP_BLUE = colors.HexColor("#1e3a8a")
STP_GRAY = colors.HexColor("#475569")
STP_LIGHT = colors.HexColor("#eff6ff")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            name="STPTitle", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=18, leading=22,
            textColor=STP_BLUE, alignment=TA_LEFT, spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            name="STPSubtitle", parent=base["Heading2"],
            fontName="Helvetica", fontSize=11, leading=14,
            textColor=STP_GRAY, alignment=TA_LEFT, spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            name="STPH1", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=13, leading=16,
            textColor=STP_BLUE, spaceBefore=14, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            name="STPH2", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=STP_GRAY, spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            name="STPBody", parent=base["BodyText"],
            fontName="Helvetica", fontSize=10, leading=14,
            spaceAfter=8, alignment=TA_LEFT,
        ),
        "verbatim": ParagraphStyle(
            name="STPVerbatim", parent=base["BodyText"],
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=STP_BLUE, leftIndent=14, rightIndent=14,
            backColor=STP_LIGHT, borderPadding=(8, 10, 8, 10),
            spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            name="STPFooter", parent=base["BodyText"],
            fontName="Helvetica", fontSize=8, leading=10,
            textColor=STP_GRAY, alignment=TA_CENTER,
        ),
    }


def _header_table(doc_number: str, title: str, revision: str,
                  effective_date: str, owner: str, classification: str) -> Table:
    """5-row metadata block at the top of every STP doc."""
    data = [
        ["DOCUMENT NUMBER",   doc_number,        "CLASSIFICATION", classification],
        ["TITLE",             title,             "REVISION",       revision],
        ["EFFECTIVE DATE",    effective_date,    "OWNER",          owner],
    ]
    t = Table(data, colWidths=[1.4 * inch, 2.6 * inch, 1.2 * inch, 1.6 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), STP_GRAY),
        ("TEXTCOLOR", (2, 0), (2, -1), STP_GRAY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, -1), STP_LIGHT),
        ("BOX",  (0, 0), (-1, -1), 0.5, STP_BLUE),
        ("LINEABOVE", (0, 1), (-1, -1), 0.25, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _build_doc(filename: Path) -> BaseDocTemplate:
    """BaseDocTemplate with one frame, page numbers on the footer."""
    doc = BaseDocTemplate(
        str(filename), pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title=filename.stem, author="South Texas Project Nuclear Operating Company",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height, id="main",
    )

    def _on_page(canvas, doc):
        canvas.saveState()
        # Top border bar — STP slate-blue
        canvas.setFillColor(STP_BLUE)
        canvas.rect(0, LETTER[1] - 0.45 * inch, LETTER[0], 0.45 * inch, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(0.85 * inch, LETTER[1] - 0.30 * inch,
                          "STP NUCLEAR OPERATING COMPANY")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(LETTER[0] - 0.85 * inch, LETTER[1] - 0.30 * inch,
                               "Wadsworth, Texas · NRC Docket Nos. 50-498, 50-499")
        # Footer
        canvas.setFillColor(STP_GRAY)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(0.85 * inch, 0.45 * inch,
                          f"{filename.stem} · Confidential — Internal Use Only")
        canvas.drawRightString(LETTER[0] - 0.85 * inch, 0.45 * inch,
                               f"Page {doc.page}")
        canvas.setStrokeColor(STP_BLUE)
        canvas.setLineWidth(0.5)
        canvas.line(0.85 * inch, 0.62 * inch, LETTER[0] - 0.85 * inch, 0.62 * inch)
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="default", frames=[frame], onPage=_on_page)])
    return doc


# ---------------------------------------------------------------------------
# PDF 1: STP-415 Business Travel & Per-Diem Allowances (UC-1 hero)
# ---------------------------------------------------------------------------

def gen_stp415(force: bool) -> Path:
    out = OUT_DIR / "STP-415_business_travel.pdf"
    if out.exists() and not force:
        print(f"  skip (exists): {out.name}")
        return out

    s = _styles()
    doc = _build_doc(out)
    story = []
    story.append(Paragraph("Business Travel &amp; Per-Diem Allowances", s["title"]))
    story.append(Paragraph(
        "Corporate Policy STP-415 · Finance / Travel Services",
        s["subtitle"],
    ))
    story.append(_header_table(
        doc_number="STP-415",
        title="Business Travel &amp; Per-Diem Allowances",
        revision="Rev 4",
        effective_date="2024-06-01",
        owner="STP Finance / Travel Services",
        classification="PUBLIC",
    ))
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("1.0 Purpose", s["h1"]))
    story.append(Paragraph(
        "This policy establishes maximum reimbursement amounts for business travel "
        "and on-site meeting per-diem expenses, in conformance with IRS publication 463 "
        "and 10 CFR 50 record-retention requirements.",
        s["body"],
    ))

    story.append(Paragraph("2.0 Scope", s["h1"]))
    story.append(Paragraph(
        "Applies to all STP employees and contractors authorized to incur business "
        "travel expenses on behalf of South Texas Project Nuclear Operating Company.",
        s["body"],
    ))

    story.append(Paragraph("3.0 Allowances", s["h1"]))
    story.append(Paragraph("3.1 Lodging", s["h2"]))
    story.append(Paragraph(
        "Lodging at on-site business meetings shall be reimbursed at actual cost "
        "up to the GSA per-diem rate for the locality. Receipts required.",
        s["body"],
    ))

    story.append(Paragraph("3.2 Meal Allowance", s["h2"]))
    story.append(Paragraph(
        "Per-diem meal allowance for on-site business meetings shall not exceed "
        "<b>$75.00 per traveler per calendar day</b>, inclusive of gratuity.",
        s["verbatim"],
    ))
    story.append(Paragraph(
        "Itemized receipts are required for any single meal exceeding $40. "
        "The allowance is split as: $25 breakfast / $25 lunch / $25 dinner.",
        s["body"],
    ))

    story.append(Paragraph("3.3 Incidental Expenses", s["h2"]))
    story.append(Paragraph(
        "Incidental expenses (parking, tolls, business calls) shall be reimbursed "
        "at actual cost with itemized receipts.",
        s["body"],
    ))

    story.append(Paragraph("4.0 Approval Authority", s["h1"]))
    story.append(Paragraph(
        "Director-level approval is required for travel exceeding $2,500 per trip. "
        "Vice-President approval is required for international travel.",
        s["body"],
    ))

    story.append(Paragraph("5.0 Records Retention", s["h1"]))
    story.append(Paragraph(
        "Travel expense records shall be retained for seven (7) years per "
        "STP-001 General Records Retention Schedule.",
        s["body"],
    ))

    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "<i>End of STP-415 Rev 4 · Effective 2024-06-01</i>",
        s["footer"],
    ))

    doc.build(story)
    print(f"  ✓ wrote {out.name}")
    return out


# ---------------------------------------------------------------------------
# PDF 2: WO-2026-00871 Work Package (UC-2 hero)
# ---------------------------------------------------------------------------

def gen_work_package(force: bool) -> Path:
    out = OUT_DIR / "WO-2026-00871_work_package.pdf"
    if out.exists() and not force:
        print(f"  skip (exists): {out.name}")
        return out

    s = _styles()
    doc = _build_doc(out)
    story = []
    story.append(Paragraph("Work Package · WO-2026-00871", s["title"]))
    story.append(Paragraph(
        "Reactor Coolant Pump Bearing Inspection (PM-7B) · P-3A",
        s["subtitle"],
    ))

    # Cover sheet metadata
    cover_data = [
        ["Work Order ID",       "WO-2026-00871",          "Status",          "CLOSED"],
        ["Equipment ID",        "P-3A",                   "System",          "RCS (Reactor Coolant)"],
        ["Type",                "Preventive (PM-7B)",     "Procedure",       "0PMP-RCS-7B Rev 2"],
        ["Opened",              "2026-03-18 08:00 CST",   "Closed",          "2026-03-18 14:30 CST"],
        ["Lead Engineer",       "Diane Okafor (EMP-1042)", "Hours Charged",   "6.5 hr"],
        ["Technicians",         "Marcus Holloway (EMP-2117), Jamal Greene (EMP-2243)", "", ""],
        ["Regulatory Basis",    "TS 3.4.5 / SR 3.4.5.1",  "NRC Reportable",  "No"],
    ]
    t = Table(cover_data, colWidths=[1.4 * inch, 2.4 * inch, 1.2 * inch, 1.8 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), STP_GRAY),
        ("TEXTCOLOR", (2, 0), (2, -1), STP_GRAY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, STP_BLUE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, STP_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("SPAN", (1, 5), (3, 5)),  # Technicians cell spans
    ]))
    story.append(t)
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("1.0 Scope of Work", s["h1"]))
    story.append(Paragraph(
        "Scheduled inspection of P-3A reactor coolant pump thrust and journal "
        "bearings per procedure 0PMP-RCS-7B (Rev 2). Includes vibration baseline, "
        "bearing oil sample collection, and seal-cavity visual inspection.",
        s["body"],
    ))

    story.append(Paragraph("2.0 Pre-Job Conditions", s["h1"]))
    story.append(Paragraph(
        "Unit 1 in MODE 5 (refueling outage). RCP-3A breaker open and tagged per "
        "OSHA 1910.147. Two-person LOTO verification documented in Section 7.0.",
        s["body"],
    ))

    story.append(Paragraph("3.0 Steps Performed", s["h1"]))
    steps = [
        ["3.1", "Verify LOTO applied + RCP-3A breaker open",                     "✓ Verified by Holloway 08:14"],
        ["3.2", "Remove upper bearing housing access cover",                     "✓ Holloway 08:42"],
        ["3.3", "Visual inspection of thrust bearing (acceptance: no scoring)",  "✓ Pass — Greene 09:08"],
        ["3.4", "Vibration baseline data collection (axial + radial)",           "✓ 0.18 in/s axial — Okafor 10:15"],
        ["3.5", "Bearing oil sample collection (3 × 50ml)",                      "✓ Sample ID: BL-2026-0318-P3A-1"],
        ["3.6", "Seal-cavity visual inspection",                                 "✓ Dry — no leak signature"],
        ["3.7", "Reinstall bearing housing cover, torque to 95 ft-lbs",          "✓ Torqued + verified"],
        ["3.8", "Remove LOTO, restore RCP-3A breaker",                           "✓ 13:45 — Holloway"],
        ["3.9", "Post-maintenance functional test (50% rated speed × 30 min)",   "✓ Pass — vibration 0.21 in/s"],
    ]
    t = Table(steps, colWidths=[0.5 * inch, 4.0 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX",  (0, 0), (-1, -1), 0.5, STP_BLUE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, STP_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), STP_BLUE),
    ]))
    story.append(t)

    story.append(Paragraph("4.0 Acceptance Criteria", s["h1"]))
    story.append(Paragraph(
        "Per 0PMP-RCS-7B Section 4.0: bearing axial vibration ≤ 0.20 in/s post-maintenance "
        "(measured: 0.21 in/s — within tolerance per Engineering Disposition #ED-2026-014). "
        "Thrust play 0.020 ± 0.005 in (measured: 0.022 in — pass).",
        s["body"],
    ))

    story.append(Paragraph("5.0 Findings", s["h1"]))
    story.append(Paragraph(
        "No abnormal indications. Bearing surface shows expected wear pattern consistent "
        "with 730-day service interval. No corrective action required at this time. "
        "Next PM-7B due 2027-06-17 per pm_schedule.",
        s["body"],
    ))

    story.append(Paragraph("6.0 Sign-Offs", s["h1"]))
    sign_data = [
        ["Role",            "Name",            "Employee ID", "Date / Time"],
        ["Lead Engineer",   "Diane Okafor",    "EMP-1042",   "2026-03-18 14:30"],
        ["Technician",      "Marcus Holloway", "EMP-2117",   "2026-03-18 14:25"],
        ["Technician",      "Jamal Greene",    "EMP-2243",   "2026-03-18 14:25"],
        ["Operations Rev.", "Sarah Mendez",    "EMP-1188",   "2026-03-18 15:02"],
        ["QA Verification", "Tony Garcia",     "EMP-0871",   "2026-03-18 16:14"],
    ]
    t = Table(sign_data, colWidths=[1.5 * inch, 2.0 * inch, 1.2 * inch, 1.8 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), STP_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), STP_BLUE),
        ("BOX",  (0, 0), (-1, -1), 0.5, STP_BLUE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, STP_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ wrote {out.name}")
    return out


# ---------------------------------------------------------------------------
# PDF 3: 0PMP-RCS-7B Procedure (UC-2/UC-4 hero)
# ---------------------------------------------------------------------------

def gen_procedure(force: bool) -> Path:
    out = OUT_DIR / "0PMP-RCS-7B_procedure.pdf"
    if out.exists() and not force:
        print(f"  skip (exists): {out.name}")
        return out

    s = _styles()
    doc = _build_doc(out)
    story = []
    story.append(Paragraph(
        "RCP Bearing Inspection &amp; Replacement (PM-7B)", s["title"]))
    story.append(Paragraph(
        "Preventive Maintenance Procedure 0PMP-RCS-7B · Maintenance / Mechanical",
        s["subtitle"],
    ))
    story.append(_header_table(
        doc_number="0PMP-RCS-7B",
        title="RCP Bearing Inspection &amp; Replacement",
        revision="Rev 2",
        effective_date="2024-09-01",
        owner="Maintenance / Mechanical",
        classification="INTERNAL",
    ))
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("1.0 Scope", s["h1"]))
    story.append(Paragraph(
        "This procedure governs the scheduled inspection of RCP thrust and journal "
        "bearings on Westinghouse Model-93A reactor coolant pumps at intervals of "
        "<b>730 days</b>, in conformance with Tech Spec 3.4.5 and ASME Section XI.",
        s["body"],
    ))

    story.append(Paragraph("2.0 Prerequisites", s["h1"]))
    story.append(Paragraph(
        "• Unit shall be in MODE 5 (refueling) or MODE 6 (defueled) prior to procedure entry.<br/>"
        "• RCP breaker shall be open with two-person LOTO verification per OSHA 1910.147.<br/>"
        "• Bearing oil sample collection equipment available (3 × 50ml clean sample bottles).<br/>"
        "• Calibrated vibration data collector (calibration current within 30 days).",
        s["body"],
    ))

    story.append(Paragraph("3.0 Personnel Qualifications", s["h1"]))
    story.append(Paragraph(
        "Lead engineer shall hold ASME Section XI Inspector certification. "
        "Technicians shall hold Mechanical Maintenance II minimum.",
        s["body"],
    ))

    story.append(Paragraph("4.0 Acceptance Criteria", s["h1"]))
    story.append(Paragraph(
        "Bearing axial vibration shall be ≤ 0.20 in/s post-maintenance; thrust play "
        "shall be 0.020 ± 0.005 in. Out-of-spec readings require Engineering Disposition.",
        s["verbatim"],
    ))

    story.append(Paragraph("5.0 Procedure Steps", s["h1"]))
    story.append(Paragraph(
        "5.1 Verify LOTO applied. Two-person verification documented on attached sign-off form.<br/><br/>"
        "5.2 Remove upper bearing housing access cover. Inspect for cracks, deformation.<br/><br/>"
        "5.3 Visually inspect thrust bearing surfaces. Acceptance: no scoring, pitting, or unusual wear.<br/><br/>"
        "5.4 Collect vibration baseline data — axial and radial channels — with calibrated meter.<br/><br/>"
        "5.5 Collect three 50ml bearing oil samples for chemistry analysis. Label with sample ID format BL-YYYY-MMDD-&lt;eq&gt;-&lt;n&gt;.<br/><br/>"
        "5.6 Visually inspect mechanical seal cavity. Acceptance: no leak signature, no oil staining.<br/><br/>"
        "5.7 Reinstall bearing housing cover. Torque to <b>95 ft-lbs ± 5</b> per Westinghouse specification.<br/><br/>"
        "5.8 Remove LOTO and restore RCP breaker.<br/><br/>"
        "5.9 Perform post-maintenance functional test: 50% rated speed × 30 min. Acceptable if vibration meets §4.0 criteria.",
        s["body"],
    ))

    story.append(Paragraph("6.0 Records", s["h1"]))
    story.append(Paragraph(
        "Completed work package shall be filed in eDM under WO-YYYY-NNNNN. "
        "Bearing oil sample chemistry results shall be filed in chemistry record CR-RCS-&lt;equipment&gt;-&lt;date&gt;. "
        "Records retained per 10 CFR 50.71 and STP-001.",
        s["body"],
    ))

    story.append(Paragraph("7.0 References", s["h1"]))
    story.append(Paragraph(
        "• Tech Spec 3.4.5 — Reactor Coolant System Operability<br/>"
        "• ASME Section XI — Rules for In-Service Inspection<br/>"
        "• Westinghouse RCP Maintenance Manual, Section 7.4<br/>"
        "• OSHA 1910.147 — Lockout/Tagout<br/>"
        "• STP-OP-2204 — Reactor Coolant Pump Surveillance &amp; Lockout",
        s["body"],
    ))

    doc.build(story)
    print(f"  ✓ wrote {out.name}")
    return out


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing PDFs")
    args = ap.parse_args()

    print(f"Hero PDF generator → {OUT_DIR}")
    gen_stp415(args.force)
    gen_work_package(args.force)
    gen_procedure(args.force)
    print(f"\nGenerated 3 hero PDFs in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
