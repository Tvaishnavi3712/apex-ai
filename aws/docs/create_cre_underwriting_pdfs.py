"""
Generate Commercial Real Estate Underwriting Submission PDFs
Comprehensive 5-6 page test documents for insurance underwriting demo
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.piecharts import Pie
import os

OUTPUT_DIR = '/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/synthetic-data/insurance/commercial_real_estate'

def create_cre_submission_pdf(filename, data):
    """Create a comprehensive Commercial Real Estate underwriting submission PDF."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=12, textColor=colors.darkblue)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceBefore=16, spaceAfter=8, textColor=colors.darkblue, borderPadding=4)
    subsection_style = ParagraphStyle('Subsection', parent=styles['Heading3'], fontSize=11, spaceBefore=10, spaceAfter=6, textColor=colors.black)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=14)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')

    elements = []

    # ========== PAGE 1: COVER & APPLICANT INFO ==========

    # Header
    elements.append(Paragraph("COMMERCIAL PROPERTY INSURANCE", title_style))
    elements.append(Paragraph("Underwriting Submission Package", ParagraphStyle('Subtitle', alignment=TA_CENTER, fontSize=14, textColor=colors.grey, spaceAfter=20)))
    elements.append(Spacer(1, 10))

    # Submission Info Box
    submission_info = [
        ['Submission ID:', data['submission_id'], 'Submission Date:', data['submission_date']],
        ['Broker:', data['broker_name'], 'Broker License:', data['broker_license']],
        ['Requested Effective:', data['effective_date'], 'Requested Expiry:', data['expiry_date']],
    ]
    info_table = Table(submission_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.98)),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Named Insured Section
    elements.append(Paragraph("1. NAMED INSURED INFORMATION", section_style))

    insured_data = [
        ['Legal Entity Name:', data['insured_name']],
        ['DBA (if applicable):', data['insured_dba']],
        ['Entity Type:', data['entity_type']],
        ['Tax ID / EIN:', data['tax_id']],
        ['Years in Business:', data['years_in_business']],
        ['Mailing Address:', data['mailing_address']],
        ['Primary Contact:', data['primary_contact']],
        ['Contact Phone:', data['contact_phone']],
        ['Contact Email:', data['contact_email']],
    ]
    insured_table = Table(insured_data, colWidths=[2*inch, 5*inch])
    insured_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
    ]))
    elements.append(insured_table)
    elements.append(Spacer(1, 15))

    # Coverage Requested Section
    elements.append(Paragraph("2. COVERAGE REQUESTED", section_style))

    coverage_data = [
        ['Coverage Type', 'Limit', 'Deductible', 'Co-Insurance'],
        ['Building Coverage', f"${data['building_limit']:,}", f"${data['building_deductible']:,}", f"{data['coinsurance']}%"],
        ['Business Personal Property', f"${data['bpp_limit']:,}", f"${data['bpp_deductible']:,}", f"{data['coinsurance']}%"],
        ['Business Income', f"${data['bi_limit']:,}", f"{data['bi_waiting_period']} days", 'N/A'],
        ['General Liability', f"${data['gl_limit']:,}", f"${data['gl_deductible']:,}", 'N/A'],
        ['Umbrella/Excess', f"${data['umbrella_limit']:,}", f"${data['umbrella_retention']:,}", 'N/A'],
    ]
    coverage_table = Table(coverage_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    coverage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(coverage_table)

    elements.append(PageBreak())

    # ========== PAGE 2: PROPERTY DETAILS ==========

    elements.append(Paragraph("3. PROPERTY SCHEDULE", section_style))

    for i, prop in enumerate(data['properties'], 1):
        elements.append(Paragraph(f"Property {i}: {prop['address']}", subsection_style))

        prop_details = [
            ['Property Type:', prop['property_type'], 'Occupancy:', prop['occupancy']],
            ['Year Built:', str(prop['year_built']), 'Total Sq Ft:', f"{prop['square_feet']:,}"],
            ['Number of Stories:', str(prop['stories']), 'Construction Type:', prop['construction']],
            ['Roof Type:', prop['roof_type'], 'Roof Age:', f"{prop['roof_age']} years"],
            ['Sprinklered:', prop['sprinklered'], 'Fire Alarm:', prop['fire_alarm']],
            ['Security System:', prop['security'], 'Distance to Fire Hydrant:', prop['hydrant_distance']],
        ]
        prop_table = Table(prop_details, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        prop_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.97, 0.97, 0.97)),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(prop_table)
        elements.append(Spacer(1, 8))

        # Property values
        values_data = [
            ['Building Value:', f"${prop['building_value']:,}"],
            ['Contents Value:', f"${prop['contents_value']:,}"],
            ['Business Income (12 mo):', f"${prop['bi_value']:,}"],
            ['Total Insurable Value (TIV):', f"${prop['tiv']:,}"],
        ]
        values_table = Table(values_data, colWidths=[2*inch, 2*inch])
        values_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.darkblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(values_table)
        elements.append(Spacer(1, 15))

    # Total Portfolio Summary
    total_tiv = sum(p['tiv'] for p in data['properties'])
    elements.append(Paragraph(f"<b>TOTAL PORTFOLIO TIV: ${total_tiv:,}</b>", ParagraphStyle('Total', fontSize=12, alignment=TA_RIGHT, textColor=colors.darkblue)))

    elements.append(PageBreak())

    # ========== PAGE 3: LOSS HISTORY & RISK FACTORS ==========

    elements.append(Paragraph("4. LOSS HISTORY (Past 5 Years)", section_style))

    if data['losses']:
        loss_data = [['Date', 'Type', 'Description', 'Paid', 'Reserved', 'Status']]
        for loss in data['losses']:
            loss_data.append([
                loss['date'],
                loss['type'],
                loss['description'],
                f"${loss['paid']:,}",
                f"${loss['reserved']:,}",
                loss['status']
            ])
        loss_data.append(['', '', 'TOTAL:', f"${sum(l['paid'] for l in data['losses']):,}", f"${sum(l['reserved'] for l in data['losses']):,}", ''])

        loss_table = Table(loss_data, colWidths=[0.9*inch, 0.9*inch, 2.2*inch, 1*inch, 1*inch, 0.8*inch])
        loss_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
            ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.darkblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(loss_table)
    else:
        elements.append(Paragraph("No losses reported in the past 5 years.", body_style))

    elements.append(Spacer(1, 20))

    # Risk Factors
    elements.append(Paragraph("5. RISK ASSESSMENT FACTORS", section_style))

    risk_data = [
        ['Factor', 'Status', 'Details'],
        ['Flood Zone', data['flood_zone'], data['flood_zone_detail']],
        ['Earthquake Zone', data['eq_zone'], data['eq_zone_detail']],
        ['Hurricane Exposure', data['hurricane_exposure'], data['hurricane_detail']],
        ['Crime Rate (Area)', data['crime_rate'], data['crime_detail']],
        ['Building Code Compliance', data['code_compliance'], data['code_detail']],
        ['Prior Insurance', data['prior_insurance'], data['prior_carrier']],
    ]
    risk_table = Table(risk_data, colWidths=[1.8*inch, 1.2*inch, 4*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.3, 0.5)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(risk_table)

    elements.append(PageBreak())

    # ========== PAGE 4: TENANT SCHEDULE & FINANCIALS ==========

    elements.append(Paragraph("6. TENANT SCHEDULE", section_style))

    tenant_data = [['Tenant Name', 'Suite', 'Sq Ft', 'Lease Expiry', 'Annual Rent', 'Industry']]
    for tenant in data['tenants']:
        tenant_data.append([
            tenant['name'],
            tenant['suite'],
            f"{tenant['sqft']:,}",
            tenant['lease_expiry'],
            f"${tenant['annual_rent']:,}",
            tenant['industry']
        ])
    tenant_data.append(['TOTALS', '', f"{sum(t['sqft'] for t in data['tenants']):,}", '', f"${sum(t['annual_rent'] for t in data['tenants']):,}", ''])

    tenant_table = Table(tenant_data, colWidths=[2*inch, 0.6*inch, 0.8*inch, 1*inch, 1.2*inch, 1.4*inch])
    tenant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.darkblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.95)),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(tenant_table)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>Occupancy Rate: {data['occupancy_rate']}%</b>", body_style))

    elements.append(Spacer(1, 15))

    # Financial Summary
    elements.append(Paragraph("7. FINANCIAL SUMMARY", section_style))

    financial_data = [
        ['Metric', 'Current Year', 'Prior Year'],
        ['Gross Rental Income', f"${data['gross_income']:,}", f"${data['gross_income_prior']:,}"],
        ['Operating Expenses', f"${data['operating_expenses']:,}", f"${data['operating_expenses_prior']:,}"],
        ['Net Operating Income (NOI)', f"${data['noi']:,}", f"${data['noi_prior']:,}"],
        ['Debt Service', f"${data['debt_service']:,}", f"${data['debt_service_prior']:,}"],
        ['Debt Service Coverage Ratio', f"{data['dscr']}x", f"{data['dscr_prior']}x"],
        ['Cap Rate', f"{data['cap_rate']}%", f"{data['cap_rate_prior']}%"],
    ]
    fin_table = Table(financial_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.3)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(fin_table)

    elements.append(PageBreak())

    # ========== PAGE 5: UNDERWRITING CONSIDERATIONS ==========

    elements.append(Paragraph("8. UNDERWRITING CONSIDERATIONS", section_style))

    # Strengths
    elements.append(Paragraph("Positive Factors:", subsection_style))
    for strength in data['strengths']:
        elements.append(Paragraph(f"+ {strength}", body_style))

    elements.append(Spacer(1, 10))

    # Concerns
    elements.append(Paragraph("Risk Concerns:", subsection_style))
    for concern in data['concerns']:
        elements.append(Paragraph(f"- {concern}", body_style))

    elements.append(Spacer(1, 15))

    # Pricing Indication
    elements.append(Paragraph("9. PRICING INDICATION REQUEST", section_style))

    pricing_data = [
        ['Coverage', 'Target Premium', 'Expiring Premium'],
        ['Property (All Risk)', f"${data['target_property_premium']:,}", f"${data['expiring_property_premium']:,}"],
        ['General Liability', f"${data['target_gl_premium']:,}", f"${data['expiring_gl_premium']:,}"],
        ['Umbrella', f"${data['target_umbrella_premium']:,}", f"${data['expiring_umbrella_premium']:,}"],
        ['TOTAL', f"${data['target_total_premium']:,}", f"${data['expiring_total_premium']:,}"],
    ]
    pricing_table = Table(pricing_data, colWidths=[3*inch, 2*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.darkblue),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.95)),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(pricing_table)

    elements.append(PageBreak())

    # ========== PAGE 6: ATTACHMENTS & CERTIFICATION ==========

    elements.append(Paragraph("10. SUPPORTING DOCUMENTS ATTACHED", section_style))

    docs_list = [
        "Property Appraisal Report (dated within 12 months)",
        "Building Inspection Report",
        "Rent Roll (current month)",
        "Profit & Loss Statement (trailing 12 months)",
        "Prior Policy Declarations Page",
        "Loss Runs (5 years)",
        "Photos of Property (exterior and common areas)",
        "Certificate of Occupancy",
        "Fire Alarm & Sprinkler Certifications",
    ]
    for doc_item in docs_list:
        elements.append(Paragraph(f"[ ] {doc_item}", body_style))

    elements.append(Spacer(1, 20))

    # Broker Certification
    elements.append(Paragraph("11. BROKER CERTIFICATION", section_style))

    cert_text = """I hereby certify that the information contained in this submission is true and accurate to the best of my knowledge.
    I have conducted reasonable due diligence on the applicant and the properties described herein. I understand that any material
    misrepresentation may void coverage or result in policy rescission."""
    elements.append(Paragraph(cert_text, body_style))
    elements.append(Spacer(1, 20))

    sig_data = [
        ['Broker Signature:', '_' * 40, 'Date:', '_' * 20],
        ['Print Name:', data['broker_name'], 'License #:', data['broker_license']],
        ['Agency:', data['broker_agency'], 'Phone:', data['broker_phone']],
    ]
    sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph("CONFIDENTIAL - FOR UNDERWRITING PURPOSES ONLY", ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=colors.grey)))
    elements.append(Paragraph(f"Submission ID: {data['submission_id']} | Generated: {data['submission_date']}", ParagraphStyle('Footer2', alignment=TA_CENTER, fontSize=8, textColor=colors.grey)))

    doc.build(elements)
    print(f"Created: {filepath}")


# ============ TEST DATA SETS ============

# Submission 1: Standard Office Building - GOOD RISK (Auto-Approve candidate)
submission_01 = {
    'submission_id': 'CRE-2024-00142',
    'submission_date': 'March 12, 2024',
    'effective_date': 'April 1, 2024',
    'expiry_date': 'April 1, 2025',
    'broker_name': 'Michael Stevens',
    'broker_license': 'CA-INS-7834521',
    'broker_agency': 'Pacific Coast Insurance Brokers',
    'broker_phone': '(415) 555-0892',

    'insured_name': 'Meridian Office Partners LLC',
    'insured_dba': 'Meridian Business Center',
    'entity_type': 'Limited Liability Company',
    'tax_id': '94-3847562',
    'years_in_business': '12',
    'mailing_address': '100 Montgomery Street, Suite 2400, San Francisco, CA 94104',
    'primary_contact': 'Jennifer Walsh, Managing Partner',
    'contact_phone': '(415) 555-1200',
    'contact_email': 'jwalsh@meridianpartners.com',

    'building_limit': 25000000,
    'building_deductible': 25000,
    'bpp_limit': 2000000,
    'bpp_deductible': 10000,
    'bi_limit': 4000000,
    'bi_waiting_period': 72,
    'gl_limit': 2000000,
    'gl_deductible': 5000,
    'umbrella_limit': 10000000,
    'umbrella_retention': 10000,
    'coinsurance': 90,

    'properties': [
        {
            'address': '500 California Street, San Francisco, CA 94104',
            'property_type': 'Class A Office Building',
            'occupancy': 'Professional Offices',
            'year_built': 2008,
            'square_feet': 125000,
            'stories': 12,
            'construction': 'Fire Resistive (ISO Class 6)',
            'roof_type': 'Built-up with gravel',
            'roof_age': 8,
            'sprinklered': 'Yes - Full NFPA 13',
            'fire_alarm': 'Central Station Monitored',
            'security': '24/7 Guard + CCTV',
            'hydrant_distance': '150 feet',
            'building_value': 22000000,
            'contents_value': 1500000,
            'bi_value': 3500000,
            'tiv': 27000000,
        }
    ],

    'losses': [],  # No losses - clean history

    'flood_zone': 'Zone X',
    'flood_zone_detail': 'Minimal flood hazard area - no flood insurance required',
    'eq_zone': 'Zone 3',
    'eq_zone_detail': 'Moderate seismic activity - earthquake coverage recommended',
    'hurricane_exposure': 'Low',
    'hurricane_detail': 'Pacific Coast - minimal hurricane/windstorm exposure',
    'crime_rate': 'Low',
    'crime_detail': 'Financial District - well-patrolled, low crime statistics',
    'code_compliance': 'Full',
    'code_detail': 'Building meets all current codes, elevator modernization completed 2022',
    'prior_insurance': 'Continuous',
    'prior_carrier': 'Hartford Fire Insurance - 5 years, no lapses',

    'tenants': [
        {'name': 'Morrison & Associates LLP', 'suite': '1200', 'sqft': 25000, 'lease_expiry': '2027-12-31', 'annual_rent': 1250000, 'industry': 'Law Firm'},
        {'name': 'Pacific Wealth Advisors', 'suite': '800', 'sqft': 18000, 'lease_expiry': '2026-06-30', 'annual_rent': 900000, 'industry': 'Financial Services'},
        {'name': 'TechStart Ventures', 'suite': '1000', 'sqft': 22000, 'lease_expiry': '2028-03-31', 'annual_rent': 1100000, 'industry': 'Venture Capital'},
        {'name': 'Bay Area Medical Group', 'suite': '500', 'sqft': 15000, 'lease_expiry': '2025-09-30', 'annual_rent': 750000, 'industry': 'Healthcare'},
        {'name': 'CloudFirst Technologies', 'suite': '600', 'sqft': 20000, 'lease_expiry': '2026-12-31', 'annual_rent': 1000000, 'industry': 'Technology'},
    ],
    'occupancy_rate': 96,

    'gross_income': 5800000,
    'gross_income_prior': 5500000,
    'operating_expenses': 1740000,
    'operating_expenses_prior': 1650000,
    'noi': 4060000,
    'noi_prior': 3850000,
    'debt_service': 2200000,
    'debt_service_prior': 2200000,
    'dscr': 1.85,
    'dscr_prior': 1.75,
    'cap_rate': 6.2,
    'cap_rate_prior': 6.0,

    'strengths': [
        'Class A office building in prime Financial District location',
        'Strong tenant roster with creditworthy occupants',
        '96% occupancy rate with weighted average lease term of 3.2 years',
        'No loss history in past 5 years',
        'Full sprinkler system and modern fire/life safety systems',
        'Experienced property management with strong financials (DSCR 1.85x)',
    ],
    'concerns': [
        'Earthquake exposure - recommend EQ coverage sublimit',
        'One tenant (Bay Area Medical) lease expires in 18 months',
    ],

    'target_property_premium': 85000,
    'expiring_property_premium': 82000,
    'target_gl_premium': 15000,
    'expiring_gl_premium': 14500,
    'target_umbrella_premium': 12000,
    'expiring_umbrella_premium': 11500,
    'target_total_premium': 112000,
    'expiring_total_premium': 108000,
}

# Submission 2: Mixed-Use Development - MODERATE RISK (Refer to Underwriter)
submission_02 = {
    'submission_id': 'CRE-2024-00187',
    'submission_date': 'March 12, 2024',
    'effective_date': 'April 15, 2024',
    'expiry_date': 'April 15, 2025',
    'broker_name': 'Sarah Chen',
    'broker_license': 'FL-INS-9923847',
    'broker_agency': 'Southeast Commercial Insurance',
    'broker_phone': '(305) 555-7721',

    'insured_name': 'Bayshore Mixed-Use Development LLC',
    'insured_dba': 'Bayshore Towne Center',
    'entity_type': 'Limited Liability Company',
    'tax_id': '59-7283945',
    'years_in_business': '6',
    'mailing_address': '2200 Brickell Avenue, Suite 1100, Miami, FL 33129',
    'primary_contact': 'Carlos Rodriguez, Development Manager',
    'contact_phone': '(305) 555-4400',
    'contact_email': 'crodriguez@bayshoredevelopment.com',

    'building_limit': 45000000,
    'building_deductible': 50000,
    'bpp_limit': 5000000,
    'bpp_deductible': 25000,
    'bi_limit': 8000000,
    'bi_waiting_period': 72,
    'gl_limit': 5000000,
    'gl_deductible': 10000,
    'umbrella_limit': 25000000,
    'umbrella_retention': 25000,
    'coinsurance': 80,

    'properties': [
        {
            'address': '1500 Bayshore Drive, Miami, FL 33132',
            'property_type': 'Mixed-Use (Retail/Office/Residential)',
            'occupancy': 'Ground Floor Retail, Floors 2-5 Office, Floors 6-20 Residential',
            'year_built': 2019,
            'square_feet': 285000,
            'stories': 20,
            'construction': 'Fire Resistive (ISO Class 6)',
            'roof_type': 'Modified bitumen',
            'roof_age': 5,
            'sprinklered': 'Yes - Full NFPA 13',
            'fire_alarm': 'Central Station Monitored',
            'security': '24/7 Concierge + CCTV',
            'hydrant_distance': '100 feet',
            'building_value': 42000000,
            'contents_value': 4500000,
            'bi_value': 7500000,
            'tiv': 54000000,
        }
    ],

    'losses': [
        {'date': '2022-09-28', 'type': 'Wind/Hail', 'description': 'Hurricane Ian - roof damage and water intrusion', 'paid': 185000, 'reserved': 0, 'status': 'Closed'},
        {'date': '2023-04-15', 'type': 'Water', 'description': 'Burst pipe in 12th floor residential unit', 'paid': 45000, 'reserved': 0, 'status': 'Closed'},
    ],

    'flood_zone': 'Zone AE',
    'flood_zone_detail': 'HIGH RISK - Base flood elevation 8 feet, flood insurance required',
    'eq_zone': 'Zone 0',
    'eq_zone_detail': 'Minimal seismic activity',
    'hurricane_exposure': 'High',
    'hurricane_detail': 'Coastal Miami - significant windstorm exposure, within 1 mile of coast',
    'crime_rate': 'Moderate',
    'crime_detail': 'Urban area with typical metro crime statistics',
    'code_compliance': 'Full',
    'code_detail': 'Built to Miami-Dade hurricane code, impact-resistant windows',
    'prior_insurance': 'Continuous',
    'prior_carrier': 'Citizens Property Insurance - 3 years',

    'tenants': [
        {'name': 'Whole Foods Market', 'suite': 'G100', 'sqft': 35000, 'lease_expiry': '2034-08-31', 'annual_rent': 1400000, 'industry': 'Grocery'},
        {'name': 'CorePower Yoga', 'suite': 'G200', 'sqft': 8000, 'lease_expiry': '2027-02-28', 'annual_rent': 240000, 'industry': 'Fitness'},
        {'name': 'First National Bank', 'suite': '200', 'sqft': 12000, 'lease_expiry': '2029-12-31', 'annual_rent': 480000, 'industry': 'Banking'},
        {'name': 'Coastal Law Partners', 'suite': '300', 'sqft': 15000, 'lease_expiry': '2026-06-30', 'annual_rent': 525000, 'industry': 'Legal'},
        {'name': 'Residential Units (180)', 'suite': 'Floors 6-20', 'sqft': 162000, 'lease_expiry': 'Various', 'annual_rent': 5400000, 'industry': 'Residential'},
    ],
    'occupancy_rate': 88,

    'gross_income': 9200000,
    'gross_income_prior': 8800000,
    'operating_expenses': 3680000,
    'operating_expenses_prior': 3520000,
    'noi': 5520000,
    'noi_prior': 5280000,
    'debt_service': 4200000,
    'debt_service_prior': 4200000,
    'dscr': 1.31,
    'dscr_prior': 1.26,
    'cap_rate': 5.8,
    'cap_rate_prior': 5.5,

    'strengths': [
        'Modern construction built to Miami-Dade hurricane code',
        'Strong anchor tenant (Whole Foods) with 10+ year lease',
        'Diversified income stream from retail, office, and residential',
        'Full sprinkler and fire/life safety systems',
        'Property management experienced with mixed-use operations',
    ],
    'concerns': [
        'HIGH FLOOD ZONE (AE) - significant flood exposure',
        'Hurricane exposure - prior loss from Hurricane Ian ($185K)',
        'Water damage claim in 2023 indicates potential maintenance issues',
        'Lower DSCR (1.31x) - tighter financial cushion',
        '88% occupancy - below market average for the area',
        'Prior carrier (Citizens) is insurer of last resort',
    ],

    'target_property_premium': 285000,
    'expiring_property_premium': 265000,
    'target_gl_premium': 45000,
    'expiring_gl_premium': 42000,
    'target_umbrella_premium': 38000,
    'expiring_umbrella_premium': 35000,
    'target_total_premium': 368000,
    'expiring_total_premium': 342000,
}

# Submission 3: Industrial Warehouse - HIGH RISK (Decline or Significant Restrictions)
submission_03 = {
    'submission_id': 'CRE-2024-00203',
    'submission_date': 'March 12, 2024',
    'effective_date': 'May 1, 2024',
    'expiry_date': 'May 1, 2025',
    'broker_name': 'Robert Thompson',
    'broker_license': 'TX-INS-5567234',
    'broker_agency': 'Lone Star Commercial Insurance',
    'broker_phone': '(713) 555-3300',

    'insured_name': 'Gulf Coast Warehouse Holdings LP',
    'insured_dba': 'Port Industrial Complex',
    'entity_type': 'Limited Partnership',
    'tax_id': '76-8834521',
    'years_in_business': '8',
    'mailing_address': '4500 Navigation Blvd, Houston, TX 77011',
    'primary_contact': 'David Martinez, General Partner',
    'contact_phone': '(713) 555-8800',
    'contact_email': 'dmartinez@gulfcoastwarehouse.com',

    'building_limit': 18000000,
    'building_deductible': 100000,
    'bpp_limit': 8000000,
    'bpp_deductible': 50000,
    'bi_limit': 3000000,
    'bi_waiting_period': 72,
    'gl_limit': 2000000,
    'gl_deductible': 25000,
    'umbrella_limit': 5000000,
    'umbrella_retention': 50000,
    'coinsurance': 80,

    'properties': [
        {
            'address': '8700 Port Road, Houston, TX 77029',
            'property_type': 'Industrial Warehouse/Distribution',
            'occupancy': 'Chemical Storage & Distribution',
            'year_built': 1985,
            'square_feet': 175000,
            'stories': 1,
            'construction': 'Non-Combustible (ISO Class 3)',
            'roof_type': 'Metal deck',
            'roof_age': 22,
            'sprinklered': 'Partial - Office areas only',
            'fire_alarm': 'Local alarm only',
            'security': 'Perimeter fence + night watchman',
            'hydrant_distance': '450 feet',
            'building_value': 12000000,
            'contents_value': 6500000,
            'bi_value': 2800000,
            'tiv': 21300000,
        },
        {
            'address': '8750 Port Road, Houston, TX 77029',
            'property_type': 'Industrial Warehouse',
            'occupancy': 'General Warehousing',
            'year_built': 1978,
            'square_feet': 85000,
            'stories': 1,
            'construction': 'Joisted Masonry (ISO Class 2)',
            'roof_type': 'Built-up tar and gravel',
            'roof_age': 31,
            'sprinklered': 'No',
            'fire_alarm': 'None',
            'security': 'Perimeter fence only',
            'hydrant_distance': '500+ feet',
            'building_value': 4500000,
            'contents_value': 1200000,
            'bi_value': 500000,
            'tiv': 6200000,
        }
    ],

    'losses': [
        {'date': '2020-08-27', 'type': 'Wind/Flood', 'description': 'Hurricane Laura - significant roof and water damage', 'paid': 892000, 'reserved': 0, 'status': 'Closed'},
        {'date': '2021-02-18', 'type': 'Freeze', 'description': 'Winter Storm Uri - pipe burst and equipment damage', 'paid': 445000, 'reserved': 0, 'status': 'Closed'},
        {'date': '2022-06-12', 'type': 'Fire', 'description': 'Electrical fire in Building B - contained to one section', 'paid': 178000, 'reserved': 25000, 'status': 'Open'},
        {'date': '2023-11-03', 'type': 'Theft', 'description': 'Break-in and theft of copper wiring and equipment', 'paid': 67000, 'reserved': 0, 'status': 'Closed'},
    ],

    'flood_zone': 'Zone A',
    'flood_zone_detail': 'HIGH RISK - Within 500-year floodplain, near Houston Ship Channel',
    'eq_zone': 'Zone 0',
    'eq_zone_detail': 'Minimal seismic activity',
    'hurricane_exposure': 'High',
    'hurricane_detail': 'Gulf Coast exposure - within 50 miles of coast',
    'crime_rate': 'High',
    'crime_detail': 'Industrial area with elevated theft and vandalism statistics',
    'code_compliance': 'Partial',
    'code_detail': 'Building B has outstanding fire code violations - sprinkler required by 2025',
    'prior_insurance': 'Gaps',
    'prior_carrier': 'Multiple carriers - 2 non-renewals in past 3 years',

    'tenants': [
        {'name': 'ChemDistro Inc.', 'suite': 'Bldg A', 'sqft': 120000, 'lease_expiry': '2025-04-30', 'annual_rent': 840000, 'industry': 'Chemical Distribution'},
        {'name': 'Gulf Logistics LLC', 'suite': 'Bldg A', 'sqft': 55000, 'lease_expiry': '2024-12-31', 'annual_rent': 330000, 'industry': 'Logistics'},
        {'name': 'VACANT', 'suite': 'Bldg B', 'sqft': 85000, 'lease_expiry': 'N/A', 'annual_rent': 0, 'industry': 'N/A'},
    ],
    'occupancy_rate': 67,

    'gross_income': 1420000,
    'gross_income_prior': 1850000,
    'operating_expenses': 710000,
    'operating_expenses_prior': 740000,
    'noi': 710000,
    'noi_prior': 1110000,
    'debt_service': 680000,
    'debt_service_prior': 680000,
    'dscr': 1.04,
    'dscr_prior': 1.63,
    'cap_rate': 4.1,
    'cap_rate_prior': 6.4,

    'strengths': [
        'Long-term tenant ChemDistro has been in place 6 years',
        'Strategic location near Port of Houston',
        'Owner committed to installing sprinklers in Building B by Q4 2024',
    ],
    'concerns': [
        'SIGNIFICANT LOSS HISTORY - 4 claims totaling $1.58M in 4 years',
        'HIGH FLOOD ZONE (A) - near Ship Channel, recurring flood exposure',
        'Building B is unsprinklered with outstanding fire code violations',
        'Older roof on Building B (31 years) - past useful life',
        '67% occupancy - Building B entirely vacant',
        'Chemical storage occupancy - hazardous materials exposure',
        'Weak DSCR (1.04x) - minimal financial cushion',
        'Prior non-renewals indicate adverse selection risk',
        'Limited fire protection - local alarm only, far from hydrant',
        'High crime area with recent theft claim',
    ],

    'target_property_premium': 425000,
    'expiring_property_premium': 380000,
    'target_gl_premium': 85000,
    'expiring_gl_premium': 75000,
    'target_umbrella_premium': 65000,
    'expiring_umbrella_premium': 55000,
    'target_total_premium': 575000,
    'expiring_total_premium': 510000,
}

# Generate all PDFs
print("Generating Commercial Real Estate Underwriting Submission PDFs...")
print("=" * 60)

create_cre_submission_pdf('submission_01_office_good_risk.pdf', submission_01)
create_cre_submission_pdf('submission_02_mixed_use_moderate_risk.pdf', submission_02)
create_cre_submission_pdf('submission_03_industrial_high_risk.pdf', submission_03)

print("=" * 60)
print(f"\nAll PDFs created in: {OUTPUT_DIR}")
print("\nTest Scenarios:")
print("1. submission_01_office_good_risk.pdf      -> AUTO-APPROVE (clean history, strong financials)")
print("2. submission_02_mixed_use_moderate_risk.pdf -> REFER TO UNDERWRITER (flood zone, prior losses)")
print("3. submission_03_industrial_high_risk.pdf  -> DECLINE/RESTRICT (significant losses, code violations)")
