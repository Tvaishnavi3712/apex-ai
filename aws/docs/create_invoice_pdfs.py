"""
Generate Sample Invoice PDFs for Demo Testing
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os

OUTPUT_DIR = '/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/synthetic-data/invoices/demo'

def create_invoice_pdf(filename, invoice_data):
    """Create a professional invoice PDF."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER, spaceAfter=20)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)

    elements = []

    # Title
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 20))

    # Vendor and Bill To
    vendor_info = f"""<b>{invoice_data['vendor_name']}</b><br/>
{invoice_data['vendor_address']}<br/>
Tax ID: {invoice_data['vendor_tax_id']}<br/>
Phone: {invoice_data['vendor_phone']}<br/>
Email: {invoice_data['vendor_email']}"""

    bill_to = f"""<b>BILL TO:</b><br/>
<b>Apex Financial Corp</b><br/>
500 Enterprise Way<br/>
San Francisco, CA 94105"""

    header_table = Table([
        [Paragraph(vendor_info, header_style), Paragraph(bill_to, header_style)]
    ], colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 30))

    # Invoice Details Box
    details_data = [
        ['Invoice Number:', invoice_data['invoice_number']],
        ['Invoice Date:', invoice_data['invoice_date']],
        ['Due Date:', invoice_data['due_date']],
        ['PO Number:', invoice_data['po_number']],
        ['Payment Terms:', invoice_data['payment_terms']],
    ]
    details_table = Table(details_data, colWidths=[1.5*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 30))

    # Line Items Table
    line_items_header = ['Description', 'Qty', 'Unit Price', 'Amount']
    line_items_data = [line_items_header] + invoice_data['line_items']

    # Add totals
    line_items_data.append(['', '', 'Subtotal:', f"${invoice_data['subtotal']:,.2f}"])
    line_items_data.append(['', '', f"Tax ({invoice_data['tax_rate']}):", f"${invoice_data['tax_amount']:,.2f}"])
    line_items_data.append(['', '', 'TOTAL DUE:', f"${invoice_data['total']:,.2f}"])

    items_table = Table(line_items_data, colWidths=[3.5*inch, 0.75*inch, 1.25*inch, 1.25*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        # Body
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -4), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -4), 0.5, colors.grey),
        # Totals section
        ('FONTNAME', (2, -3), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 40))

    # Footer
    footer_text = "Thank you for your business! Payment can be made via ACH, wire transfer, or check."
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=10, textColor=colors.grey)))

    doc.build(elements)
    print(f"Created: {filepath}")

# Invoice 1: Auto-Approve
create_invoice_pdf('invoice_01_auto_approve.pdf', {
    'vendor_name': 'QuickPrint Solutions',
    'vendor_address': '1234 Commerce Drive, Austin, TX 78701',
    'vendor_tax_id': '87-1234567',
    'vendor_phone': '(512) 555-0123',
    'vendor_email': 'billing@quickprint.com',
    'invoice_number': 'QPS-2024-0156',
    'invoice_date': 'March 10, 2024',
    'due_date': 'April 9, 2024',
    'po_number': 'PO-2024-0089',
    'payment_terms': 'Net 30',
    'line_items': [
        ['Business cards (500 ct)', '2', '$45.00', '$90.00'],
        ['Letterhead paper (ream)', '5', '$28.00', '$140.00'],
        ['Company brochures (100 ct)', '3', '$85.00', '$255.00'],
        ['Envelope printing (box)', '2', '$62.00', '$124.00'],
    ],
    'subtotal': 609.00,
    'tax_rate': '8.25%',
    'tax_amount': 50.24,
    'total': 659.24
})

# Invoice 2: Manager Approval
create_invoice_pdf('invoice_02_manager_approval.pdf', {
    'vendor_name': 'Acme Office Supplies',
    'vendor_address': '9876 Industrial Blvd, Chicago, IL 60601',
    'vendor_tax_id': '36-9876543',
    'vendor_phone': '(312) 555-0456',
    'vendor_email': 'accounts@acmeoffice.com',
    'invoice_number': 'AOS-2024-0892',
    'invoice_date': 'March 11, 2024',
    'due_date': 'April 10, 2024',
    'po_number': 'PO-2024-7834',
    'payment_terms': 'Net 30',
    'line_items': [
        ['Ergonomic Office Chair - Premium', '10', '$150.00', '$1,500.00'],
        ['Standing Desk - Electric Adjustable', '5', '$400.00', '$2,000.00'],
        ['Monitor Arm - Dual Mount', '8', '$75.00', '$600.00'],
        ['Keyboard Tray - Adjustable', '10', '$45.00', '$450.00'],
    ],
    'subtotal': 4550.00,
    'tax_rate': '8.25%',
    'tax_amount': 375.38,
    'total': 4925.38
})

# Invoice 3: Director Approval
create_invoice_pdf('invoice_03_director_approval.pdf', {
    'vendor_name': 'TechServe IT Solutions',
    'vendor_address': '2500 Innovation Park, Seattle, WA 98101',
    'vendor_tax_id': '91-5555123',
    'vendor_phone': '(206) 555-0789',
    'vendor_email': 'invoicing@techserve.com',
    'invoice_number': 'TS-2024-3347',
    'invoice_date': 'March 12, 2024',
    'due_date': 'April 11, 2024',
    'po_number': 'PO-2024-4521',
    'payment_terms': 'Net 30',
    'line_items': [
        ['Dell PowerEdge Server R750', '2', '$8,500.00', '$17,000.00'],
        ['Cisco Catalyst Switch 9300', '4', '$2,200.00', '$8,800.00'],
        ['APC Smart-UPS 3000VA', '2', '$1,450.00', '$2,900.00'],
        ['Installation & Configuration', '1', '$3,500.00', '$3,500.00'],
    ],
    'subtotal': 32200.00,
    'tax_rate': '8.25%',
    'tax_amount': 2656.50,
    'total': 34856.50
})

# Invoice 4: VP Approval
create_invoice_pdf('invoice_04_vp_approval.pdf', {
    'vendor_name': 'Global Cloud Partners LLC',
    'vendor_address': 'One Cloud Center, Suite 4500, New York, NY 10001',
    'vendor_tax_id': '13-7777999',
    'vendor_phone': '(212) 555-0999',
    'vendor_email': 'enterprise@globalcloud.com',
    'invoice_number': 'GCP-2024-0088',
    'invoice_date': 'March 12, 2024',
    'due_date': 'April 11, 2024',
    'po_number': 'PO-2024-1001',
    'payment_terms': 'Net 30',
    'line_items': [
        ['Enterprise Cloud Platform License (500 seats)', '1', '$45,000.00', '$45,000.00'],
        ['Premium Support Package (24/7)', '1', '$12,000.00', '$12,000.00'],
        ['Data Migration Services', '1', '$8,500.00', '$8,500.00'],
        ['Security & Compliance Add-on', '1', '$6,500.00', '$6,500.00'],
        ['Training (40 hours)', '1', '$4,000.00', '$4,000.00'],
    ],
    'subtotal': 76000.00,
    'tax_rate': '8.25%',
    'tax_amount': 6270.00,
    'total': 82270.00
})

# Invoice 5: Missing PO
create_invoice_pdf('invoice_05_missing_po.pdf', {
    'vendor_name': 'Metro Catering Services',
    'vendor_address': '789 Culinary Lane, San Francisco, CA 94102',
    'vendor_tax_id': '94-8888222',
    'vendor_phone': '(415) 555-0333',
    'vendor_email': 'events@metrocatering.com',
    'invoice_number': 'MCS-2024-0445',
    'invoice_date': 'March 8, 2024',
    'due_date': 'March 22, 2024',
    'po_number': 'N/A',
    'payment_terms': 'Net 15',
    'line_items': [
        ['Corporate Event Catering (75 guests)', '1', '$2,800.00', '$2,800.00'],
        ['Premium Beverage Package', '1', '$650.00', '$650.00'],
        ['Event Setup & Breakdown', '1', '$400.00', '$400.00'],
        ['Gratuity (18%)', '1', '$693.00', '$693.00'],
    ],
    'subtotal': 4543.00,
    'tax_rate': '8.625%',
    'tax_amount': 391.83,
    'total': 4934.83
})

# Invoice 6: New Vendor
create_invoice_pdf('invoice_06_new_vendor.pdf', {
    'vendor_name': 'Bright Ideas Marketing Agency',
    'vendor_address': '456 Creative Blvd, Los Angeles, CA 90028',
    'vendor_tax_id': '95-1112223',
    'vendor_phone': '(323) 555-0777',
    'vendor_email': 'billing@brightideas.agency',
    'invoice_number': 'BI-2024-0012',
    'invoice_date': 'March 11, 2024',
    'due_date': 'April 10, 2024',
    'po_number': 'PO-2024-8899',
    'payment_terms': 'Net 30',
    'line_items': [
        ['Brand Strategy Workshop', '1', '$3,500.00', '$3,500.00'],
        ['Logo Design Package', '1', '$2,500.00', '$2,500.00'],
        ['Brand Guidelines Document', '1', '$1,800.00', '$1,800.00'],
        ['Social Media Templates (10)', '1', '$950.00', '$950.00'],
    ],
    'subtotal': 8750.00,
    'tax_rate': '9.5%',
    'tax_amount': 831.25,
    'total': 9581.25
})

print("\nAll invoice PDFs created successfully!")
print(f"Location: {OUTPUT_DIR}")
