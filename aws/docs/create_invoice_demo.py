"""
Generate APEX Demo Script Word Document - Invoice Processing
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

def create_demo_script():
    doc = Document()

    # Title
    title = doc.add_heading('APEX AI Platform - Live Demo Script', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph('Invoice Processing: From Document to Payment Approval in Minutes')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].bold = True
    subtitle.runs[0].font.size = Pt(14)

    doc.add_paragraph()

    # Executive Summary
    doc.add_heading('EXECUTIVE SUMMARY', level=1)

    summary = doc.add_paragraph()
    summary.add_run('Demo Objective: ').bold = True
    summary.add_run('Show how APEX transforms manual invoice processing into AI-powered automation - extracting data, validating vendors, matching POs, and routing for approval - all without writing code.')

    doc.add_paragraph()

    # Use Case Box
    doc.add_heading('Use Case: Accounts Payable Invoice Processing', level=2)

    problem = doc.add_paragraph()
    problem.add_run('The Problem:\n').bold = True
    problem.add_run('• Finance teams manually process 500+ invoices monthly\n')
    problem.add_run('• Each invoice takes 10-15 minutes to review and route\n')
    problem.add_run('• Error rate of 5-8% leads to payment delays and vendor disputes\n')
    problem.add_run('• Month-end close delayed waiting for invoice processing')

    solution = doc.add_paragraph()
    solution.add_run('The Solution:\n').bold = True
    solution.add_run('APEX InvoiceBot extracts, validates, and routes invoices in under 30 seconds with 98%+ accuracy')

    doc.add_paragraph()

    # Value Props
    doc.add_heading('Key Value Propositions', level=2)
    props = doc.add_paragraph()
    props.add_run('1. Your Infrastructure').bold = True
    props.add_run(' - Data never leaves your AWS account\n')
    props.add_run('2. No Code Required').bold = True
    props.add_run(' - Business users design workflows in plain English\n')
    props.add_run('3. Production Ready').bold = True
    props.add_run(' - Built-in validation, audit trails, and compliance\n')
    props.add_run('4. Enterprise Scale').bold = True
    props.add_run(' - Process thousands of invoices per day')

    doc.add_page_break()

    # Pre-Demo Checklist
    doc.add_heading('PRE-DEMO CHECKLIST', level=1)
    checklist = doc.add_paragraph()
    checklist.add_run('□ Servers running (Frontend: localhost:3000, Backend: localhost:8000)\n')
    checklist.add_run('□ Sample invoice documents ready\n')
    checklist.add_run('□ Browser open to APEX Dashboard\n')
    checklist.add_run('□ InvoiceBot agent deployed and active\n')
    checklist.add_run('□ Notepad ready for audience questions')

    doc.add_paragraph()

    # Demo Script
    doc.add_heading('DEMO SCRIPT (15-20 Minutes)', level=1)

    # ACT 1
    doc.add_heading('ACT 1: The Problem (2 minutes)', level=2)

    talking = doc.add_paragraph()
    talking.add_run('[TALKING POINT]\n').bold = True
    talking.add_run('"Let me show you what Accounts Payable teams deal with every day."')
    talking.style = 'Quote'

    say1 = doc.add_paragraph()
    say1.add_run('SAY:\n').bold = True
    say1.add_run('"Meet Maria, an AP specialist at a mid-size manufacturing company. Every day, she receives invoices from 200+ vendors - some emailed as PDFs, some faxed, some arriving through vendor portals.\n\n')
    say1.add_run('For each invoice, she must:\n')
    say1.add_run('1. Open the document and extract key data\n')
    say1.add_run('2. Look up the vendor in the system\n')
    say1.add_run('3. Match it to a purchase order\n')
    say1.add_run('4. Verify the math (line items, taxes, totals)\n')
    say1.add_run('5. Route it for the right approval level\n\n')
    say1.add_run('This takes 10-15 minutes per invoice. At 40 invoices per day, Maria spends her entire week on data entry instead of exception handling and vendor relationships."')

    pause = doc.add_paragraph()
    pause.add_run('[PAUSE]\n').bold = True
    pause.add_run('SAY: "What if Maria had an AI agent that could handle all that data extraction and routing automatically? Let\'s build that agent right now."')

    doc.add_page_break()

    # ACT 2
    doc.add_heading('ACT 2: The APEX Dashboard (1 minute)', level=2)

    nav = doc.add_paragraph()
    nav.add_run('[Navigate to: http://localhost:3000]\n').bold = True

    say2 = doc.add_paragraph()
    say2.add_run('SAY:\n').bold = True
    say2.add_run('"This is APEX AI Platform - the command center for your AI workforce.\n\n')
    say2.add_run('On the left, you see our main modules:\n')
    say2.add_run('• Canvas - where we design AI workflows\n')
    say2.add_run('• Agents - our deployed AI workers\n')
    say2.add_run('• Actions - the tools our agents can use\n')
    say2.add_run('• Agent Hub - where humans collaborate with AI\n')
    say2.add_run('• Command Center - real-time monitoring\n\n')
    say2.add_run('Let me show you how we build an invoice processing agent from scratch."')

    doc.add_paragraph()

    # ACT 3
    doc.add_heading('ACT 3: Create the Blueprint (3 minutes)', level=2)

    nav3 = doc.add_paragraph()
    nav3.add_run('[Navigate to: Canvas → Blueprints tab → New Blueprint]\n').bold = True

    say3 = doc.add_paragraph()
    say3.add_run('SAY:\n').bold = True
    say3.add_run('"First, we teach APEX what an invoice looks like. We call this a Blueprint - it\'s the AI\'s understanding of a document type."')

    step1 = doc.add_paragraph()
    step1.add_run('Step 1: Click "New Blueprint"\n').bold = True
    step1.add_run('SAY: "I\'ll name this \'Vendor Invoice\' and select Financial Services as the industry."')

    step2 = doc.add_paragraph()
    step2.add_run('Step 2: Define fields (type these live):\n').bold = True

    fields = doc.add_paragraph()
    fields.add_run('''
Blueprint Name: Vendor Invoice
Industry: Financial Services
Description: Extract structured data from vendor invoices for AP processing

Fields:
1. invoice_number (string) - The unique invoice identifier
2. invoice_date (date) - Date the invoice was issued
3. due_date (date) - Payment due date
4. po_number (string) - Purchase order reference
5. vendor_name (string) - Name of the vendor company
6. vendor_tax_id (string) - Vendor's tax ID or EIN
7. bill_to_name (string) - Company being billed
8. line_items (array) - Description, quantity, unit price, amount
9. subtotal (number) - Sum of line items before tax
10. tax_amount (number) - Total tax
11. total_amount (number) - Final invoice total
''')
    fields.style = 'No Spacing'

    say3b = doc.add_paragraph()
    say3b.add_run('SAY:\n').bold = True
    say3b.add_run('"Notice I\'m using plain English to describe each field. No regex patterns, no code - just descriptions like \'the unique invoice identifier\' or \'date the invoice was issued.\'\n\n')
    say3b.add_run('The AI will use these instructions to find and extract the right data from any invoice format."')

    step3 = doc.add_paragraph()
    step3.add_run('Step 3: Click "Save Blueprint"\n').bold = True
    step3.add_run('SAY: "That\'s it. APEX now understands invoices. This blueprint will be used by Amazon Bedrock to extract these fields from any invoice - typed, handwritten, or scanned."')

    doc.add_page_break()

    # ACT 4
    doc.add_heading('ACT 4: Create the Playbook (4 minutes)', level=2)

    nav4 = doc.add_paragraph()
    nav4.add_run('[Navigate to: Canvas → Playbooks tab → New Playbook]\n').bold = True

    say4 = doc.add_paragraph()
    say4.add_run('SAY:\n').bold = True
    say4.add_run('"Now we tell our AI agent what to DO with the extracted data. We call this a Playbook - written in plain English."')

    step4_1 = doc.add_paragraph()
    step4_1.add_run('Step 1: Click "New Playbook"\n').bold = True

    step4_2 = doc.add_paragraph()
    step4_2.add_run('Step 2: Fill in the playbook:\n').bold = True

    playbook = doc.add_paragraph()
    playbook.add_run('''
Playbook Name: Invoice Processing
Industry: Financial Services
Blueprint: Vendor Invoice

Intent:
Process incoming vendor invoices by extracting data, validating against
vendor records, matching to purchase orders, and routing for appropriate
approval based on amount thresholds.

Business Rules:
• Invoices under $1,000 auto-approve
• $1,000 - $10,000 require manager approval
• $10,000 - $50,000 require director approval
• Over $50,000 require VP Finance approval
• All invoices must have matching PO for amounts over $1,000
• Duplicate invoices are rejected automatically

Recipe:
## Step 1: Extract Invoice Data
Use the Vendor Invoice blueprint to extract all fields from the document.

## Step 2: Validate Vendor
Look up the vendor in our approved vendor database.
If vendor not found, flag for vendor onboarding.

## Step 3: Check for Duplicates
Verify this invoice number hasn't been processed before.
If duplicate found, reject with notification.

## Step 4: Match Purchase Order
For invoices over $1,000, find the matching PO.
Verify invoice amount is within 5% of PO amount.

## Step 5: Route for Approval
Based on invoice amount, route to appropriate approver:
- Under $1,000: AUTO-APPROVE
- $1,000-$10,000: Route to Manager
- $10,000-$50,000: Route to Director
- Over $50,000: Route to VP Finance

## Step 6: Generate Response
Return structured output with decision and next steps.
''')
    playbook.style = 'No Spacing'

    say4b = doc.add_paragraph()
    say4b.add_run('SAY:\n').bold = True
    say4b.add_run('"Look at this - I\'m writing business logic in plain English. These are the same rules Maria follows, just written down for the AI.\n\n')
    say4b.add_run('No Python, no YAML syntax to memorize. I\'m describing the workflow exactly as I\'d explain it to a new employee."')

    step4_3 = doc.add_paragraph()
    step4_3.add_run('Step 3: Click "Save Playbook"\n').bold = True

    doc.add_page_break()

    # ACT 5
    doc.add_heading('ACT 5: Deploy the Agent (2 minutes)', level=2)

    nav5 = doc.add_paragraph()
    nav5.add_run('[Navigate to: Agents → Create Agent]\n').bold = True

    say5 = doc.add_paragraph()
    say5.add_run('SAY:\n').bold = True
    say5.add_run('"Now let\'s bring our playbook to life by deploying it as an AI agent."')

    config = doc.add_paragraph()
    config.add_run('Configuration:\n').bold = True
    config.add_run('''
Agent Name: InvoiceBot
Playbook: Invoice Processing
Runtime: AWS Bedrock AgentCore
Status: Active
''')

    say5b = doc.add_paragraph()
    say5b.add_run('SAY:\n').bold = True
    say5b.add_run('"I\'m connecting our playbook to AWS Bedrock AgentCore. This means InvoiceBot runs inside YOUR AWS account - your invoice data never leaves your infrastructure.\n\n')
    say5b.add_run('This is critical for financial compliance - SOC 2, PCI-DSS, all handled."')

    step5 = doc.add_paragraph()
    step5.add_run('Step: Click "Deploy"\n').bold = True
    step5.add_run('SAY: "The agent is deploying. Notice what we DIDN\'T do:\n')
    step5.add_run('• No code written\n')
    step5.add_run('• No servers configured\n')
    step5.add_run('• No ML pipelines set up\n\n')
    step5.add_run('We just described what we wanted in plain English."')

    doc.add_paragraph()

    # ACT 6
    doc.add_heading('ACT 6: Test with Standard Invoice (2 minutes)', level=2)

    nav6 = doc.add_paragraph()
    nav6.add_run('[Navigate to: Agent Hub → Select InvoiceBot]\n').bold = True

    say6 = doc.add_paragraph()
    say6.add_run('SAY:\n').bold = True
    say6.add_run('"Let\'s test InvoiceBot with a real invoice."')

    test1 = doc.add_paragraph()
    test1.add_run('Type this in the chat:\n').bold = True
    test1.add_run('''
Process this invoice:
Vendor: Acme Office Supplies
Invoice #: INV-2024-0892
Invoice Date: March 10, 2024
PO Number: PO-7834
Line Items:
- Office chairs (10) @ $150 each = $1,500
- Standing desks (5) @ $400 each = $2,000
Subtotal: $3,500
Tax (8%): $280
Total: $3,780
''')

    wait = doc.add_paragraph()
    wait.add_run('[Wait for response]\n').bold = True

    say6b = doc.add_paragraph()
    say6b.add_run('SAY:\n').bold = True
    say6b.add_run('"Watch what happens. The agent is:\n')
    say6b.add_run('1. Extracting the invoice data\n')
    say6b.add_run('2. Looking up Acme Office Supplies in our vendor database\n')
    say6b.add_run('3. Checking for duplicate invoice numbers\n')
    say6b.add_run('4. Matching to PO-7834\n')
    say6b.add_run('5. Routing based on the $3,780 amount"\n\n')
    say6b.add_run('[Read the response]\n\n')
    say6b.add_run('SAY: "The agent routed this to Manager approval because:\n')
    say6b.add_run('• Amount is between $1,000 and $10,000\n')
    say6b.add_run('• Vendor is active in our system\n')
    say6b.add_run('• No duplicate found\n')
    say6b.add_run('• PO match confirmed\n\n')
    say6b.add_run('What took Maria 10 minutes, the AI did in 3 seconds."')

    doc.add_page_break()

    # ACT 7
    doc.add_heading('ACT 7: Test Edge Cases (2 minutes)', level=2)

    say7 = doc.add_paragraph()
    say7.add_run('SAY:\n').bold = True
    say7.add_run('"Let\'s see how it handles exceptions."')

    test2 = doc.add_paragraph()
    test2.add_run('Type this:\n').bold = True
    test2.add_run('''
New invoice from Global Tech Solutions:
Invoice #: GT-2024-5521
Amount: $75,000
No PO number provided
Service: Annual software license renewal
''')

    wait2 = doc.add_paragraph()
    wait2.add_run('[Wait for response]\n').bold = True

    say7b = doc.add_paragraph()
    say7b.add_run('SAY:\n').bold = True
    say7b.add_run('"This one is different. The agent flagged it because:\n')
    say7b.add_run('• Amount over $50,000 requires VP Finance approval\n')
    say7b.add_run('• No PO number - needs exception handling\n')
    say7b.add_run('• High-value transaction requires additional validation\n\n')
    say7b.add_run('The AI isn\'t trying to replace Maria - it\'s handling the routine 80% so she can focus on exceptions like this."')

    doc.add_paragraph()

    # ACT 8
    doc.add_heading('ACT 8: The Value Proposition (2 minutes)', level=2)

    nav8 = doc.add_paragraph()
    nav8.add_run('[Return to Dashboard]\n').bold = True

    say8 = doc.add_paragraph()
    say8.add_run('SAY:\n').bold = True
    say8.add_run('"Let\'s recap what we just did in 15 minutes:\n\n')
    say8.add_run('1. Created a Blueprint - taught AI to understand invoices\n')
    say8.add_run('2. Wrote a Playbook - defined processing rules in plain English\n')
    say8.add_run('3. Deployed an Agent - launched to production on AWS\n')
    say8.add_run('4. Tested Live - processed real invoices with real decisions\n\n')
    say8.add_run('The Business Impact:\n')
    say8.add_run('• Maria processes 400+ invoices per day instead of 40\n')
    say8.add_run('• Average handling time: 15 minutes → 30 seconds\n')
    say8.add_run('• Error rate: 5-8% → less than 1%\n')
    say8.add_run('• Month-end close: 3 days faster\n\n')
    say8.add_run('The Technical Reality:\n')
    say8.add_run('• Zero code written\n')
    say8.add_run('• Data never left your AWS account\n')
    say8.add_run('• Full audit trail for compliance\n')
    say8.add_run('• Scale up instantly for month-end volume"')

    doc.add_page_break()

    # Q&A
    doc.add_heading('Q&A - Common Questions', level=1)

    qa = [
        ('Q: "What AI models are you using?"',
         'A: "We use Amazon Bedrock - specifically Amazon Nova and Claude models. The architecture supports any model, including fine-tuned models on your own invoice formats."'),
        ('Q: "How accurate is the extraction?"',
         'A: "Out of the box, 92-95% on standard invoices. With fine-tuning on your specific vendor formats, we\'ve seen 98%+ accuracy."'),
        ('Q: "What about PII and financial data security?"',
         'A: "All processing happens inside your AWS VPC. We don\'t see your data - APEX is the orchestration layer, not the data layer. SOC 2 and PCI-DSS compliant."'),
        ('Q: "Can it integrate with our ERP?"',
         'A: "Yes - through our Actions module. We have pre-built connectors for SAP, Oracle, NetSuite, QuickBooks, and custom APIs."'),
        ('Q: "What about different invoice formats?"',
         'A: "That\'s the power of AI extraction. Whether it\'s a PDF, scanned image, or email attachment - the blueprint handles format variations automatically."'),
    ]

    for q, a in qa:
        qp = doc.add_paragraph()
        qp.add_run(q + '\n').bold = True
        qp.add_run(a)
        doc.add_paragraph()

    doc.add_page_break()

    # Technical Appendix
    doc.add_heading('TECHNICAL APPENDIX', level=1)

    urls = doc.add_paragraph()
    urls.add_run('URLs:\n').bold = True
    urls.add_run('• Frontend: http://localhost:3000\n')
    urls.add_run('• Backend API: http://localhost:8000\n')
    urls.add_run('• API Docs: http://localhost:8000/docs')

    doc.add_paragraph()

    troubleshoot = doc.add_paragraph()
    troubleshoot.add_run('Emergency Troubleshooting:\n').bold = True
    troubleshoot.add_run('• If agent doesn\'t respond: Check AgentCore status in AWS Console\n')
    troubleshoot.add_run('• If extraction fails: Verify blueprint is saved correctly\n')
    troubleshoot.add_run('• If frontend crashes: Restart with npm run dev')

    doc.add_paragraph()

    # Footer
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.add_run('Document Version: 1.0 | Last Updated: March 2026 | APEX AI Platform Team')
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Save
    output_path = '/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/docs/APEX_Demo_Script_Invoice_Processing.docx'
    doc.save(output_path)
    print(f"Demo script saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_demo_script()
