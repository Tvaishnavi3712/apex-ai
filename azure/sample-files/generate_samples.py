#!/usr/bin/env python3
"""
Generate robust sample files for ApexLens upload testing.

Produces 9 files in ./sample-files/ — one per pipeline the UI supports:

  01-Order_Mod_Request_1044.pdf        → Zero-Touch Order Modification (CBB Demo 1)
  generated/02-QC_Batch_50_Certificates.zip → QC Batch Ingestion & Hold (CBB Demo 2)
  03-Port_Strike_Alert_VinylResin.xml  → Disruption Impact & Reroute   (CBB Demo 3)
  04-Invoice_Globex_GLX-2024-0441.pdf  → Invoice Processing & Validation
  05-Claim_CL-8821_WaterDamage.pdf     → Claims Intake & Triage
  06-PO_Acme_4421_Rush.pdf             → PO Auto-Approval
  07-QC_Report_Batch_2024-B.pdf        → QC Report Triage
  08-Contract_GulfCoast_CTR-2026.pdf   → Contract Clause Review
  09-SupplyAlert_VinylResin.xml        → Supply Alert Broadcast

The filenames match guessPipelineForFilename() in frontend/src/pages/apex-lens.tsx
so dropping them into the upload dialog auto-selects the right pipeline.
"""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.pdfgen import canvas


HERE = Path(__file__).parent
STYLES = getSampleStyleSheet()

TITLE    = ParagraphStyle("Title",    parent=STYLES["Title"],   fontName="Helvetica-Bold", fontSize=18, textColor=colors.HexColor("#0f172a"), spaceAfter=6)
H2       = ParagraphStyle("H2",       parent=STYLES["Heading2"],fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#1f2937"), spaceBefore=10, spaceAfter=4)
BODY     = ParagraphStyle("Body",     parent=STYLES["BodyText"],fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#111827"), leading=14)
META     = ParagraphStyle("Meta",     parent=STYLES["BodyText"],fontName="Helvetica",      fontSize=9,  textColor=colors.HexColor("#6b7280"), leading=12)
MONO     = ParagraphStyle("Mono",     parent=STYLES["BodyText"],fontName="Courier",        fontSize=9,  textColor=colors.HexColor("#111827"), leading=12)


def table(rows, col_widths, header=True, zebra=True):
    t = Table(rows, colWidths=col_widths)
    style = [
        ("FONTNAME",  (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("VALIGN",    (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.HexColor("#cbd5e1")) if header else
        ("LINEBELOW", (0, 0), (-1, -1), 0, colors.white),
    ]
    if header:
        style.extend([
            ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND",(0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ])
    if zebra and header:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))
    t.setStyle(TableStyle(style))
    return t


def build_doc(path: Path, story: list) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=path.stem.replace("_", " "),
    )
    doc.build(story)
    print(f"  ✓ {path.name:48s}  {path.stat().st_size:>7d} B")


# ─────────────────────── 01 · Order Modification PDF (CBB Demo 1) ───────────────────────

def build_order_mod():
    story = [
        Paragraph("Order Modification Request", TITLE),
        Paragraph("Midwest Window &amp; Door Supply — Gold Partner", META),
        Paragraph("Sent to orders@cornerstone-brands.com · April 21, 2026 · 09:12 ET", META),
        Spacer(1, 0.18 * inch),

        Paragraph("Original Order", H2),
        table([
            ["Order ID",          "CBB-ORD-1044"],
            ["Distributor",       "Midwest Window & Door Supply (Gold Partner)"],
            ["Product",           "Commercial Casement Window"],
            ["Product SKU",       "CCW-4860-LG"],
            ["Quantity",          "24 units"],
            ["Dimensions (W × H)","48\" × 60\""],
            ["Production Start",  "April 28, 2026"],
            ["Lead Time (orig.)", "14 business days"],
        ], col_widths=[1.6 * inch, 4.6 * inch], header=False),
        Spacer(1, 0.14 * inch),

        Paragraph("Requested Changes", H2),
        table([
            ["New Dimensions",   "48\" × 62\""],
            ["Variance",         "+3.3% height (within 5% tolerance)"],
            ["Quantity",         "24 units (unchanged)"],
            ["Reason",           "End-customer site survey revised header height. Please confirm production accommodates +2\" height."],
            ["Requested by",     "Alex Morrison, Orders Specialist"],
            ["Contact",          "alex.morrison@midwestwindow.com · (312) 555-0144"],
        ], col_widths=[1.6 * inch, 4.6 * inch], header=False),
        Spacer(1, 0.14 * inch),

        Paragraph("Internal Use — Do Not Edit", H2),
        Paragraph(
            "This PDF was generated by the distributor portal. Field positions are stable for Azure OpenAI "
            "Data Automation blueprint <b>Order Modification Form v2.1</b>.",
            META,
        ),
    ]
    build_doc(HERE / "01-Order_Mod_Request_1044.pdf", story)


# ─────────────────────── 02 · QC Batch ZIP (CBB Demo 2) ───────────────────────

def build_qc_cert_pdf(stream: io.BytesIO, lot_id: str, supplier: str, tensile: float, spec_min: float, color_delta_e: float, pass_fail: str) -> None:
    """One QC certificate PDF. We bundle 50 of these into the ZIP."""
    c = canvas.Canvas(stream, pagesize=LETTER)
    w, h = LETTER

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 16); c.drawString(0.75 * inch, h - 0.9 * inch, "QUALITY CERTIFICATE")
    c.setFillColor(colors.HexColor("#6b7280"))
    c.setFont("Helvetica", 9);       c.drawString(0.75 * inch, h - 1.08 * inch, f"{supplier}  —  Supplier QA Lab")

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(0.75 * inch, h - 1.18 * inch, w - 0.75 * inch, h - 1.18 * inch)

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 10)
    y = h - 1.55 * inch
    for label, value in [
        ("Lot ID",             lot_id),
        ("Material",           "Vinyl Resin Compound (PVC Grade A)"),
        ("Supplier ID",        "SUP-0081"),
        ("Inspection Date",    "April 20, 2026"),
        ("Inspector",          "INS-1144"),
        ("Plant Destination",  "Ohio Plant 7"),
        ("Quantity (kg)",      "2400"),
        ("Tensile Strength",   f"{tensile:.1f} MPa"),
        ("Tensile Spec (min)", f"{spec_min:.1f} MPa"),
        ("Color ΔE",           f"{color_delta_e:.2f}"),
        ("Color Threshold",    "2.00"),
        ("Moisture %",         "0.38"),
        ("Density (g/cm³)",    "1.42"),
        ("Unit Price (USD)",   "$7.75 / kg"),
    ]:
        c.setFont("Helvetica-Bold", 10); c.drawString(0.75 * inch, y, f"{label}:")
        c.setFont("Helvetica",      10); c.drawString(2.60 * inch, y, str(value))
        y -= 0.22 * inch

    # Pass/Fail stamp
    c.setFont("Helvetica-Bold", 16)
    if pass_fail == "PASS":
        c.setFillColor(colors.HexColor("#16a34a"))
    else:
        c.setFillColor(colors.HexColor("#dc2626"))
    c.drawString(0.75 * inch, y - 0.15 * inch, f"RESULT: {pass_fail}")

    c.showPage(); c.save()


def build_qc_batch():
    out_dir = HERE / "generated"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "02-QC_Batch_50_Certificates.zip"
    passing_tensile = [40.0 + (i % 6) * 0.4 for i in range(50)]  # 40.0 .. 42.0, all ≥ 38.0 spec
    passing_delta   = [0.8 + (i % 5) * 0.15 for i in range(50)]  # 0.80 .. 1.40

    # Inject two failures per the spec
    fail_indices = {}
    fail_indices["LOT-A44"] = ("tensile",  36.5, 38.0, 1.2)   # tensile below spec
    fail_indices["LOT-B12"] = ("color",    40.1, 38.0, 2.7)   # color ΔE above threshold

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        # LOT-A01 .. LOT-A43 (43 PASS)
        for i in range(1, 44):
            lot = f"LOT-A{i:02d}"
            data = io.BytesIO()
            build_qc_cert_pdf(data, lot, "Apex Vinyl Solutions", passing_tensile[i], 38.0, passing_delta[i], "PASS")
            zf.writestr(f"QC_Cert_{lot}.pdf", data.getvalue())

        # LOT-A44 (FAIL — tensile below spec)
        data = io.BytesIO()
        _, tensile, spec, delta = fail_indices["LOT-A44"]
        build_qc_cert_pdf(data, "LOT-A44", "Apex Vinyl Solutions", tensile, spec, delta, "FAIL — tensile below spec")
        zf.writestr("QC_Cert_LOT-A44.pdf", data.getvalue())

        # LOT-A45 .. LOT-A49 (5 PASS)
        for i in range(45, 50):
            lot = f"LOT-A{i:02d}"
            data = io.BytesIO()
            build_qc_cert_pdf(data, lot, "Apex Vinyl Solutions", passing_tensile[i % 50], 38.0, passing_delta[i % 50], "PASS")
            zf.writestr(f"QC_Cert_{lot}.pdf", data.getvalue())

        # LOT-B12 (FAIL — color delta above threshold)
        data = io.BytesIO()
        _, tensile, spec, delta = fail_indices["LOT-B12"]
        build_qc_cert_pdf(data, "LOT-B12", "Apex Vinyl Solutions", tensile, spec, delta, "FAIL — color delta above threshold")
        zf.writestr("QC_Cert_LOT-B12.pdf", data.getvalue())

        # Batch manifest (plaintext alongside the PDFs)
        manifest = [
            "QC Batch Manifest — 2026-04-21",
            "Supplier:    Apex Vinyl Solutions (SUP-0081)",
            "Material:    Vinyl Resin Compound (PVC Grade A)",
            "Plant:       Ohio Plant 7",
            "Total certs: 50",
            "Expected:    48 PASS · 2 FAIL (LOT-A44 tensile, LOT-B12 color)",
        ]
        zf.writestr("MANIFEST.txt", "\n".join(manifest).encode("utf-8"))

    print(f"  ✓ {out.name:48s}  {out.stat().st_size:>7d} B   (50 PDFs + manifest)")


# ─────────────────────── 03 · Port Strike XML (CBB Demo 3) ───────────────────────

def build_port_strike():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<!--
  Disruption Alert — emitted by Global Supply Chain Monitor (GSM)
  When dropped into ApexLens, triggers the Disruption Impact & Reroute pipeline.
-->
<DisruptionAlert source="GlobalSupplyChainMonitor" version="1.0">
  <AlertID>SC-ALERT-2026-0441</AlertID>
  <EventType>PortStrike</EventType>
  <Severity>HIGH</Severity>
  <Timestamp>2026-04-21T09:08:00Z</Timestamp>

  <Port code="KSAV">
    <Name>Port of Savannah, GA</Name>
    <Country>US</Country>
    <Latitude>32.0809</Latitude>
    <Longitude>-81.0912</Longitude>
  </Port>

  <AffectedSupplier>
    <Id>SUP-0044</Id>
    <Name>Chemours Vinyl Resins</Name>
    <Tier>1</Tier>
    <PrimaryContact>
      <Name>Andrea Patel</Name>
      <Email>andrea.patel@chemours.com</Email>
    </PrimaryContact>
  </AffectedSupplier>

  <Material>
    <Id>MAT-0021</Id>
    <Name>Vinyl Resin (PVC Grade A)</Name>
    <Grade>A</Grade>
  </Material>

  <ImpactEstimate>
    <DelayDays>7</DelayDays>
    <ExpectedRecovery>2026-04-28</ExpectedRecovery>
    <SourceConfidence>0.99</SourceConfidence>
    <Region>Southeast US</Region>
  </ImpactEstimate>

  <RecommendedAction>
    <Type>RerouteAnalysis</Type>
    <Priority>IMMEDIATE</Priority>
    <RoutingTarget>logistics-alerts@cbb.com</RoutingTarget>
  </RecommendedAction>

  <Notes>
    Union escalation Day 3. No indication of settlement. Alternate suppliers
    (Oxy Vinyls LP, Formosa, PolySource) should be considered.
  </Notes>
</DisruptionAlert>
"""
    p = HERE / "03-Port_Strike_Alert_VinylResin.xml"
    p.write_text(xml, encoding="utf-8")
    print(f"  ✓ {p.name:48s}  {p.stat().st_size:>7d} B")


# ─────────────────────── 04 · Invoice PDF ───────────────────────

def build_invoice():
    story = [
        Paragraph("GLOBEX CORPORATION", TITLE),
        Paragraph("1425 Harbor Boulevard · Long Beach, CA 90802 · ap@globexcorp.com", META),
        Spacer(1, 0.18 * inch),

        Paragraph("Invoice GLX-2024-0441", H2),
        table([
            ["Invoice #",     "GLX-2024-0441"],
            ["Invoice Date",  "April 18, 2026"],
            ["Due Date",      "May 18, 2026"],
            ["PO Reference",  "PO-2024-0891"],
            ["Bill To",       "Cornerstone Building Brands\nAttn: Accounts Payable"],
            ["Payment Terms", "Net 30"],
        ], col_widths=[1.4 * inch, 4.8 * inch], header=False),
        Spacer(1, 0.18 * inch),

        Paragraph("Line Items", H2),
        table([
            ["Description", "SKU", "Qty", "Unit Price", "Line Total"],
            ["Widget A — Standard Grade",        "WID-A-STD", "200", "$180.00", "$36,000.00"],
            ["Widget B — Industrial Grade",      "WID-B-IND", "120", "$215.00", "$25,800.00"],
            ["Expedited Freight (Cold Chain)",    "SHP-COLD",  "1",  "$18,565.00","$18,565.00"],
        ], col_widths=[2.6 * inch, 1.0 * inch, 0.5 * inch, 0.9 * inch, 1.0 * inch]),
        Spacer(1, 0.08 * inch),

        table([
            ["", "", "", "Subtotal",  "$61,800.00"],
            ["", "", "", "Tax (9.5%)", "$7,035.00"],
            ["", "", "", "Total",     "$87,400.00"],
        ], col_widths=[2.6 * inch, 1.0 * inch, 0.5 * inch, 0.9 * inch, 1.0 * inch], header=False),

        Spacer(1, 0.24 * inch),
        Paragraph("Remit payment via ACH to Routing 026009593 / Acct ending 4412. Late fees accrue at 1.5%/mo.", META),
    ]
    build_doc(HERE / "04-Invoice_Globex_GLX-2024-0441.pdf", story)


# ─────────────────────── 05 · Insurance Claim PDF ───────────────────────

def build_claim():
    story = [
        Paragraph("First Notice of Loss (FNOL)", TITLE),
        Paragraph("Commercial Property — Water Damage", META),
        Spacer(1, 0.18 * inch),

        Paragraph("Claim Details", H2),
        table([
            ["Claim Number",   "CL-8821"],
            ["Policy Number",  "POL-2021-44821"],
            ["Claimant",       "Meridian Properties LLC"],
            ["Incident Date",  "April 12, 2026 · 03:20 ET"],
            ["Reported",       "April 12, 2026 · 05:40 ET"],
            ["Location",       "318 West Lincoln Ave, Suite 12, Cincinnati OH"],
            ["Incident Type",  "Interior water damage (supply-line burst)"],
            ["Claim Value",    "$142,000 (preliminary)"],
            ["Deductible",     "$5,000"],
            ["Policy Status",  "Active · no prior claims in 24 months"],
        ], col_widths=[1.6 * inch, 4.6 * inch], header=False),
        Spacer(1, 0.18 * inch),

        Paragraph("Narrative", H2),
        Paragraph(
            "At approximately 03:20 ET on April 12, a 1-inch cold-water supply line on the second floor "
            "burst at a soldered joint above suite 12. Water discharged for an estimated 90 minutes before "
            "the building engineer was able to shut off the main. Approx. 1,200 sq ft of drywall, carpet, "
            "and furniture across four rooms sustained damage. Restoration company ServiceMaster dispatched "
            "same-day for water extraction and drying.",
            BODY,
        ),
        Spacer(1, 0.12 * inch),

        Paragraph("Attachments", H2),
        Paragraph("• First-responder photos (pp. 3–7)<br/>• Moisture readings spreadsheet (p. 8)<br/>• ServiceMaster estimate ($87,400 mitigation + $54,600 reconstruction)", BODY),
    ]
    build_doc(HERE / "05-Claim_CL-8821_WaterDamage.pdf", story)


# ─────────────────────── 06 · Purchase Order PDF ───────────────────────

def build_po():
    story = [
        Paragraph("Purchase Order — PO-4421", TITLE),
        Paragraph("Issued to Acme Industrial · RUSH DELIVERY · 4-day window", META),
        Spacer(1, 0.18 * inch),

        table([
            ["PO Number",       "PO-4421"],
            ["Vendor",          "Acme Industrial"],
            ["Vendor ID",       "VND-0092"],
            ["Ordered",         "April 20, 2026"],
            ["Promised Delivery","April 24, 2026  (Rush)"],
            ["Ship To",         "Cornerstone Plant 12 · 4400 Alum Creek, Columbus OH"],
            ["Buyer",           "Jennifer Torres · procurement@cbb.com"],
        ], col_widths=[1.8 * inch, 4.4 * inch], header=False),
        Spacer(1, 0.18 * inch),

        Paragraph("Line Items", H2),
        table([
            ["SKU",       "Description",                      "Qty", "Unit",   "Total"],
            ["ACM-7701",  "Stainless fastener, M6 × 18mm",    "500", "$41.20", "$20,600.00"],
            ["ACM-7702",  "Hex bolt, 3/8\"-16 × 1-1/2\"",     "250", "$28.40", "$7,100.00"],
            ["ACM-7703",  "Flat washer, Grade 8, 5/8\" ID",   "100", "$53.00", "$5,300.00"],
        ], col_widths=[1.0 * inch, 2.6 * inch, 0.5 * inch, 0.8 * inch, 1.1 * inch]),
        Spacer(1, 0.08 * inch),
        table([
            ["", "", "", "Subtotal",        "$33,000.00"],
            ["", "", "", "Rush Surcharge",  "$1,200.00"],
            ["", "", "", "Total",           "$34,200.00"],
        ], col_widths=[1.0 * inch, 2.6 * inch, 0.5 * inch, 0.8 * inch, 1.1 * inch], header=False),
    ]
    build_doc(HERE / "06-PO_Acme_4421_Rush.pdf", story)


# ─────────────────────── 07 · QC Report PDF ───────────────────────

def build_qc_report():
    story = [
        Paragraph("Quality Control Report — Batch 2024-B", TITLE),
        Paragraph("Houston TX — Line 3 · Inspection date April 19, 2026", META),
        Spacer(1, 0.18 * inch),

        Paragraph("Summary", H2),
        table([
            ["Batch ID",         "2024-B"],
            ["Plant / Line",     "Houston TX — Line 3"],
            ["Inspection Date",  "April 19, 2026"],
            ["Units Inspected",  "2,400"],
            ["Units Passed",     "2,381"],
            ["Units Held",       "19"],
            ["Pass Rate",        "99.20%"],
            ["Hold Status",      "Partial Hold — pending re-inspection"],
            ["Inspector",        "M. Alvarez (INS-7041)"],
        ], col_widths=[1.8 * inch, 4.4 * inch], header=False),
        Spacer(1, 0.18 * inch),

        Paragraph("Defect Breakdown", H2),
        table([
            ["Defect Code", "Description",                "Units Affected", "Action"],
            ["DEF-12",      "Surface crack (cosmetic)",   "12",             "Hold for re-inspection"],
            ["DEF-07",      "Dimensional variance > 0.5%","7",              "Hold for re-inspection"],
        ], col_widths=[1.0 * inch, 2.8 * inch, 1.2 * inch, 1.6 * inch]),
        Spacer(1, 0.16 * inch),

        Paragraph("Recommendation", H2),
        Paragraph(
            "Release 2,381 passing units for shipment. Route 19 held units through secondary inspection "
            "Monday AM. Overall defect rate (0.79%) is within our 1.00% internal threshold.",
            BODY,
        ),
    ]
    build_doc(HERE / "07-QC_Report_Batch_2024-B.pdf", story)


# ─────────────────────── 08 · Vendor Contract PDF ───────────────────────

def build_contract():
    story = [
        Paragraph("Vendor Services Agreement", TITLE),
        Paragraph("CTR-2026-GC-041 · Cornerstone Building Brands ↔ Gulf Coast Logistics LLC", META),
        Spacer(1, 0.18 * inch),

        Paragraph("Key Terms", H2),
        table([
            ["Contract ID",   "CTR-2026-GC-041"],
            ["Effective",     "May 1, 2026"],
            ["Expiry",        "April 30, 2028"],
            ["Total Value",   "$4.2M over 24 months"],
            ["Auto-Renewal",  "YES — 60-day notice required (window opens Jun 1, 2027)"],
            ["Penalty Clause","2% of monthly invoice per week of SLA breach"],
            ["Governing Law", "State of Texas"],
            ["Arbitration",   "AAA · Houston TX"],
        ], col_widths=[1.8 * inch, 4.4 * inch], header=False),
        Spacer(1, 0.18 * inch),

        Paragraph("§4.2 Service Credits (excerpt)", H2),
        Paragraph(
            "If Vendor fails to meet the agreed Service Level for two consecutive reporting periods, Client "
            "may invoke the Service Credit schedule attached as Exhibit B. Service Credits shall be applied "
            "as a deduction against the next monthly invoice and shall not exceed 15% of the affected "
            "invoice in any single period.",
            BODY,
        ),
        Spacer(1, 0.10 * inch),
        Paragraph("§6.1 Termination for Cause (excerpt)", H2),
        Paragraph(
            "Either party may terminate this Agreement for material breach upon thirty (30) days' written "
            "notice if such breach is not cured within the notice period. In the event of termination under "
            "this §6.1, Vendor shall refund any prepaid fees for services not yet rendered.",
            BODY,
        ),
        Spacer(1, 0.20 * inch),
        Paragraph("Signatures on file — redacted for upload.", META),
    ]
    build_doc(HERE / "08-Contract_GulfCoast_CTR-2026.pdf", story)


# ─────────────────────── 09 · Supply Alert XML ───────────────────────

def build_supply_alert():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<SupplyAlert source="CBB-InternalMonitor">
  <AlertID>SC-ALERT-2026-0442</AlertID>
  <Severity>MEDIUM</Severity>
  <Timestamp>2026-04-21T08:55:00Z</Timestamp>

  <Component>
    <Id>VR-2201</Id>
    <Name>Vinyl Resin</Name>
  </Component>

  <Supplier>
    <Name>ChemCo Industries</Name>
    <SupplierId>SUP-0092</SupplierId>
  </Supplier>

  <DelayDays>7</DelayDays>

  <AffectedPlants>
    <Plant code="HOU">Houston</Plant>
    <Plant code="DAL">Dallas</Plant>
    <Plant code="MEM">Memphis</Plant>
  </AffectedPlants>

  <AffectedSkus count="14"/>

  <RevenueAtRiskUSD>1090000</RevenueAtRiskUSD>

  <AlternateSupplier>
    <Name>PolySource Inc</Name>
    <LeadTimeDays>3</LeadTimeDays>
    <PriceDeltaPct>15</PriceDeltaPct>
  </AlternateSupplier>

  <RecommendedAction>NotifyOpsAndSwitch</RecommendedAction>
</SupplyAlert>
"""
    p = HERE / "09-SupplyAlert_VinylResin.xml"
    p.write_text(xml, encoding="utf-8")
    print(f"  ✓ {p.name:48s}  {p.stat().st_size:>7d} B")


def main():
    print(f"\nGenerating sample files in {HERE}/\n")
    build_order_mod()
    build_qc_batch()
    build_port_strike()
    build_invoice()
    build_claim()
    build_po()
    build_qc_report()
    build_contract()
    build_supply_alert()
    print("\nDone.\n")


if __name__ == "__main__":
    main()
