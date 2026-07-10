"""
Create APEX AI Platform Demo Script Word Document
Insurance Underwriting Use Case
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT

def create_demo_document():
    doc = Document()

    # Set up styles
    style = doc.styles['Heading 1']
    style.font.size = Pt(24)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)  # Blue

    style2 = doc.styles['Heading 2']
    style2.font.size = Pt(18)
    style2.font.bold = True
    style2.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    style3 = doc.styles['Heading 3']
    style3.font.size = Pt(14)
    style3.font.bold = True

    # Title Page
    title = doc.add_heading('APEX AI Platform', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph('Live Demo Script')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = Pt(20)

    usecase = doc.add_paragraph('Insurance Underwriting Automation')
    usecase.alignment = WD_ALIGN_PARAGRAPH.CENTER
    usecase.runs[0].font.size = Pt(16)
    usecase.runs[0].font.italic = True

    doc.add_paragraph()
    doc.add_paragraph()

    # Demo info table
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    cells = [
        ('Duration:', '15-20 minutes'),
        ('Audience:', 'Business & Technical Stakeholders'),
        ('Presenter:', '[Your Name]'),
        ('Date:', 'March 2026'),
    ]
    for i, (label, value) in enumerate(cells):
        table.rows[i].cells[0].text = label
        table.rows[i].cells[1].text = value

    doc.add_page_break()

    # Executive Summary
    doc.add_heading('Executive Summary', level=1)

    doc.add_heading('Demo Objective', level=2)
    doc.add_paragraph(
        'Demonstrate how a business user can transform manual insurance underwriting '
        'into an AI-automated workflow - without writing code - in a single 15-minute session.'
    )

    doc.add_heading('The Problem We\'re Solving', level=2)
    problem_points = [
        'Manual underwriting takes 2-4 hours per application',
        'Inconsistent risk assessments across underwriters',
        'High error rate in data entry and calculations',
        'Backlog of applications waiting for review',
        'Difficulty scaling during peak seasons',
    ]
    for point in problem_points:
        doc.add_paragraph(point, style='List Bullet')

    doc.add_heading('The APEX Solution', level=2)
    solution_points = [
        'AI extracts all application data automatically (2 minutes vs 30 minutes)',
        'Consistent risk scoring using defined business rules',
        'Automatic validation and cross-referencing',
        'Human review only for edge cases and exceptions',
        'Scales instantly - process 100x more applications',
    ]
    for point in solution_points:
        doc.add_paragraph(point, style='List Bullet')

    doc.add_heading('Key Value Propositions', level=2)
    values = [
        ('Your Infrastructure', 'Data never leaves your AWS account - full compliance'),
        ('No Code Required', 'Business users design workflows in plain English'),
        ('Production Ready', 'Built-in testing, monitoring, and guardrails'),
        ('Enterprise Scale', 'Process thousands of applications per hour'),
    ]
    for title, desc in values:
        p = doc.add_paragraph()
        run = p.add_run(f'{title}: ')
        run.bold = True
        p.add_run(desc)

    doc.add_page_break()

    # Pre-Demo Checklist
    doc.add_heading('Pre-Demo Checklist', level=1)

    checklist = [
        'Servers running (Frontend: localhost:3000, Backend: localhost:8000)',
        'Browser open to APEX Dashboard',
        'Sample insurance applications ready',
        'Terminal open for any troubleshooting',
        'Notes ready for audience questions',
        'Test the full flow once before demo',
    ]
    for item in checklist:
        doc.add_paragraph(f'☐ {item}')

    doc.add_page_break()

    # Act 1
    doc.add_heading('ACT 1: The Problem (2 minutes)', level=1)

    doc.add_heading('Setting the Scene', level=2)
    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Let me introduce you to Mike. Mike is a senior underwriter at a regional insurance company. '
        'Every day, he receives a stack of insurance applications - auto, home, life, commercial. '
        'Each application needs to be:"'
    )

    steps = [
        'Opened and all data extracted manually',
        'Applicant information verified against external databases',
        'Risk factors identified and scored',
        'Premium calculated based on risk assessment',
        'Decision made: approve, decline, or refer for review',
    ]
    for i, step in enumerate(steps, 1):
        doc.add_paragraph(f'{i}. {step}')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"This process takes Mike 2-4 hours per application. On a good day, he completes 3-4 applications. '
        'The backlog grows every week. And when Mike is out sick? The whole queue stops."'
    )

    doc.add_paragraph().add_run('PAUSE, THEN SAY:').bold = True
    doc.add_paragraph(
        '"What if Mike had an AI assistant that could handle 80% of this work automatically, '
        'and only bring him the complex cases? Let\'s build that assistant right now."'
    )

    doc.add_page_break()

    # Act 2
    doc.add_heading('ACT 2: The APEX Dashboard (1 minute)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('http://localhost:3000')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"This is APEX AI Platform - the command center for your AI workforce. '
        'Think of it as a control room where business users can create, deploy, and monitor AI agents."'
    )

    doc.add_paragraph().add_run('POINT TO THE SIDEBAR AND SAY:').bold = True

    nav_items = [
        ('Canvas', 'where we design our AI workflows'),
        ('Agents', 'our deployed AI workers'),
        ('Actions', 'the tools and integrations our agents can use'),
        ('Agent Hub', 'where humans collaborate with AI'),
        ('Command Center', 'real-time monitoring and metrics'),
    ]
    for name, desc in nav_items:
        p = doc.add_paragraph()
        run = p.add_run(f'• {name}')
        run.bold = True
        p.add_run(f' - {desc}')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Let\'s create a new underwriting workflow from scratch."'
    )

    doc.add_page_break()

    # Act 3
    doc.add_heading('ACT 3: Create the Blueprint (3 minutes)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('Canvas → Blueprints tab → Click "New Blueprint"')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"First, we need to teach APEX what an insurance application looks like. '
        'We call this a Blueprint - it\'s the AI\'s understanding of a document type."'
    )

    doc.add_heading('Step 1: Basic Information', level=3)
    doc.add_paragraph().add_run('TYPE:').bold = True

    basic_info = doc.add_table(rows=3, cols=2)
    basic_info.style = 'Table Grid'
    info_data = [
        ('Blueprint Name:', 'Insurance Application'),
        ('Industry:', 'Insurance Underwriting'),
        ('Description:', 'Auto, home, and life insurance application forms'),
    ]
    for i, (label, value) in enumerate(info_data):
        basic_info.rows[i].cells[0].text = label
        basic_info.rows[i].cells[1].text = value

    doc.add_paragraph()
    doc.add_heading('Step 2: Define Fields (Type these LIVE)', level=3)

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Now I\'ll define the fields we want to extract. Notice I\'m using plain English descriptions - '
        'no code, no regex patterns."'
    )

    doc.add_paragraph().add_run('TYPE THESE FIELDS:').bold = True

    fields = [
        ('applicant_name', 'string', 'Full legal name of the insurance applicant'),
        ('date_of_birth', 'date', 'Applicant date of birth in MM/DD/YYYY format'),
        ('ssn_last_four', 'string', 'Last 4 digits of Social Security Number'),
        ('address', 'string', 'Full mailing address including city, state, zip'),
        ('policy_type', 'string', 'Type: Auto, Home, Life, or Commercial'),
        ('coverage_amount', 'number', 'Requested coverage limit in dollars'),
        ('deductible', 'number', 'Requested deductible amount'),
        ('prior_carrier', 'string', 'Name of previous insurance carrier'),
        ('claims_history', 'array', 'List of prior claims with dates and amounts'),
        ('risk_factors', 'array', 'Identified risk factors from application'),
    ]

    fields_table = doc.add_table(rows=len(fields)+1, cols=3)
    fields_table.style = 'Table Grid'
    headers = ['Field Name', 'Type', 'Description']
    for i, header in enumerate(headers):
        fields_table.rows[0].cells[i].text = header
        fields_table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
    for i, (name, ftype, desc) in enumerate(fields, 1):
        fields_table.rows[i].cells[0].text = name
        fields_table.rows[i].cells[1].text = ftype
        fields_table.rows[i].cells[2].text = desc

    doc.add_paragraph()
    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"That\'s it. Click Save. APEX now understands insurance applications. '
        'Behind the scenes, this connects to Amazon Bedrock Data Automation to extract these fields '
        'from any application - typed, handwritten, or scanned."'
    )

    doc.add_page_break()

    # Act 4
    doc.add_heading('ACT 4: Create the Playbook (4 minutes)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('Canvas → Playbooks tab → Click "New Playbook"')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Now we need to tell our AI agent what to DO with the extracted data. '
        'We call this a Playbook - the agent\'s step-by-step instructions, written in plain English."'
    )

    doc.add_heading('Step 1: Playbook Header', level=3)
    doc.add_paragraph().add_run('TYPE:').bold = True

    playbook_info = doc.add_table(rows=3, cols=2)
    playbook_info.style = 'Table Grid'
    pb_data = [
        ('Playbook Name:', 'Insurance Underwriting'),
        ('Industry:', 'Insurance Underwriting'),
        ('Blueprint:', 'Insurance Application'),
    ]
    for i, (label, value) in enumerate(pb_data):
        playbook_info.rows[i].cells[0].text = label
        playbook_info.rows[i].cells[1].text = value

    doc.add_paragraph()
    doc.add_heading('Step 2: Define Intent', level=3)
    doc.add_paragraph().add_run('TYPE:').bold = True

    intent_box = doc.add_paragraph()
    intent_box.add_run(
        'Process insurance applications by extracting applicant data, '
        'assessing risk factors, calculating premiums, and making underwriting decisions. '
        'Route complex cases to human underwriters for review.'
    )

    doc.add_paragraph()
    doc.add_heading('Step 3: Business Rules', level=3)
    doc.add_paragraph().add_run('TYPE:').bold = True

    rules = [
        'Applications with 3+ claims in past 5 years require manual review',
        'Coverage requests over $1M require senior underwriter approval',
        'Applicants under 25 get young driver surcharge for auto policies',
        'Prior policy cancellations require explanation review',
        'Credit score below 600 requires additional documentation',
    ]
    for rule in rules:
        doc.add_paragraph(f'• {rule}')

    doc.add_paragraph()
    doc.add_heading('Step 4: The Recipe (Workflow Steps)', level=3)
    doc.add_paragraph().add_run('TYPE THIS WORKFLOW:').bold = True

    workflow = """
## Step 1: Extract Application Data
Use the Insurance Application blueprint to extract all fields from the submitted document.
Validate that all required fields are present and legible.

## Step 2: Verify Applicant Information
Cross-reference applicant name and SSN with identity verification service.
Check address against USPS database for validity.
Flag any mismatches for review.

## Step 3: Assess Risk Factors
- Pull driving record for auto applications (MVR check)
- Pull property data for home applications
- Review claims history from prior carrier
- Calculate risk score based on factors

## Step 4: Apply Underwriting Rules
Check all business rules defined above.
If any rule triggers, flag for appropriate action.
Calculate base premium using rate tables.

## Step 5: Make Decision
- If risk score < 70 and no flags: AUTO-APPROVE
- If risk score 70-85: AUTO-APPROVE with conditions
- If risk score > 85 or flags present: ROUTE TO UNDERWRITER
- If coverage > $1M: ROUTE TO SENIOR UNDERWRITER

## Step 6: Generate Output
Create underwriting decision document.
Generate premium quote if approved.
Prepare applicant communication letter.
Log all decisions for audit trail.
"""
    doc.add_paragraph(workflow)

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Look at this - I\'m writing instructions the way I would explain them to a new employee. '
        'No Python, no complex syntax. Just clear business logic in plain English."'
    )

    doc.add_paragraph().add_run('Click "Save Playbook"').bold = True

    doc.add_page_break()

    # Act 5
    doc.add_heading('ACT 5: Deploy the Agent (2 minutes)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('Agents → Click "Create Agent"')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Now let\'s bring our playbook to life by deploying it as an AI agent."'
    )

    doc.add_heading('Configure the Agent', level=3)

    agent_config = doc.add_table(rows=4, cols=2)
    agent_config.style = 'Table Grid'
    agent_data = [
        ('Agent Name:', 'UnderwriteBot'),
        ('Playbook:', 'Insurance Underwriting'),
        ('Runtime:', 'AWS Bedrock AgentCore'),
        ('Status:', 'Active'),
    ]
    for i, (label, value) in enumerate(agent_data):
        agent_config.rows[i].cells[0].text = label
        agent_config.rows[i].cells[1].text = value

    doc.add_paragraph()
    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"I\'m connecting our playbook to AWS Bedrock AgentCore. This is crucial - '
        'the agent runs inside YOUR AWS account. Your applicant data, PII, everything - '
        'it never leaves your infrastructure. This is how we achieve compliance."'
    )

    doc.add_paragraph().add_run('Click "Deploy"').bold = True

    doc.add_paragraph().add_run('SAY (while deploying):').bold = True
    doc.add_paragraph(
        '"Notice what we did NOT do: We didn\'t write any code. '
        'We didn\'t configure servers. We didn\'t set up ML pipelines. '
        'We just described what we wanted in business language."'
    )

    doc.add_page_break()

    # Act 6
    doc.add_heading('ACT 6: Test the Agent LIVE (3 minutes)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('Agent Hub → Select "UnderwriteBot"')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Let\'s test our new agent with a real insurance application."'
    )

    doc.add_heading('Test Case 1: Standard Auto Application', level=3)
    doc.add_paragraph().add_run('TYPE IN CHAT:').bold = True

    test1 = doc.add_paragraph()
    test1.add_run(
        'Process this auto insurance application:\n'
        'Applicant: John Smith, DOB: 05/15/1985, SSN: XXX-XX-4532\n'
        'Address: 123 Oak Street, Columbus, OH 43215\n'
        'Policy Type: Auto Insurance\n'
        'Vehicle: 2022 Honda Accord\n'
        'Coverage Requested: $100,000 liability, $50,000 collision\n'
        'Deductible: $500\n'
        'Prior Carrier: State Farm, 5 years, no claims\n'
        'Driving Record: Clean, no violations'
    )

    doc.add_paragraph().add_run('[WAIT FOR RESPONSE]').bold = True

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Watch what happens. The agent is extracting the data, verifying the applicant, '
        'checking the driving record, calculating the risk score, and making a decision."'
    )

    doc.add_paragraph().add_run('EXPECTED RESPONSE:').bold = True
    doc.add_paragraph(
        '✓ Application AUTO-APPROVED\n'
        '• Risk Score: 45 (Low Risk)\n'
        '• Premium: $1,247/year\n'
        '• No flags triggered\n'
        '• Clean driving record verified\n'
        '• 5 years with prior carrier - loyalty discount applied'
    )

    doc.add_paragraph()
    doc.add_heading('Test Case 2: High-Risk Application (Edge Case)', level=3)
    doc.add_paragraph().add_run('TYPE IN CHAT:').bold = True

    test2 = doc.add_paragraph()
    test2.add_run(
        'Process this auto insurance application:\n'
        'Applicant: Jane Doe, DOB: 08/22/2002, SSN: XXX-XX-9876\n'
        'Address: 456 Main Ave, Cleveland, OH 44101\n'
        'Policy Type: Auto Insurance\n'
        'Vehicle: 2024 BMW M4\n'
        'Coverage Requested: $500,000 liability\n'
        'Deductible: $1,000\n'
        'Prior Carrier: None (new driver)\n'
        'Driving Record: 2 speeding tickets in past year'
    )

    doc.add_paragraph().add_run('[WAIT FOR RESPONSE]').bold = True

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"This one is different. Watch how the agent handles a more complex case..."'
    )

    doc.add_paragraph().add_run('EXPECTED RESPONSE:').bold = True
    doc.add_paragraph(
        '⚠ Application ROUTED TO UNDERWRITER\n'
        '• Risk Score: 78 (Elevated Risk)\n'
        '• Flags Triggered:\n'
        '  - Applicant under 25 (young driver)\n'
        '  - High-performance vehicle\n'
        '  - 2 violations in past 12 months\n'
        '  - No prior insurance history\n'
        '• Recommended Action: Manual review required\n'
        '• Suggested Premium Range: $4,200-5,800/year pending review'
    )

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"The AI isn\'t trying to replace underwriters - it\'s handling the routine 80% automatically '
        'so experienced underwriters like Mike can focus on complex cases like this one."'
    )

    doc.add_page_break()

    # Act 7
    doc.add_heading('ACT 7: Command Center Monitoring (2 minutes)', level=1)

    doc.add_paragraph().add_run('NAVIGATE TO:').bold = True
    doc.add_paragraph('Command Center')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"Let\'s see how our agent is performing across all applications."'
    )

    doc.add_paragraph().add_run('POINT TO METRICS:').bold = True

    metrics = [
        ('Applications Processed:', 'Real-time count of processed applications'),
        ('Success Rate:', 'Currently 98.5% - fully automated decisions'),
        ('Average Processing Time:', '45 seconds per application'),
        ('Auto-Approve Rate:', '72% of applications approved without human touch'),
        ('Escalation Rate:', '28% routed to human underwriters'),
    ]
    for metric, desc in metrics:
        p = doc.add_paragraph()
        run = p.add_run(f'• {metric}')
        run.bold = True
        p.add_run(f' {desc}')

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph(
        '"If anything goes wrong - an agent errors out, processing time spikes - we see it here immediately. '
        'Full audit trail for compliance. Every decision is logged and explainable."'
    )

    doc.add_page_break()

    # Act 8
    doc.add_heading('ACT 8: Value Summary (2 minutes)', level=1)

    doc.add_paragraph().add_run('SAY:').bold = True
    doc.add_paragraph('"Let\'s recap what we just accomplished in 15 minutes:"')

    doc.add_heading('What We Built', level=3)
    accomplishments = [
        'Created a Blueprint - Taught AI to understand insurance applications',
        'Wrote a Playbook - Defined underwriting rules in plain English',
        'Deployed an Agent - Launched to production on AWS',
        'Tested Live - Processed real applications with real decisions',
        'Monitored Results - Full visibility in Command Center',
    ]
    for i, item in enumerate(accomplishments, 1):
        doc.add_paragraph(f'{i}. {item}')

    doc.add_heading('The Business Impact', level=3)

    impact_table = doc.add_table(rows=5, cols=3)
    impact_table.style = 'Table Grid'
    impact_data = [
        ('Metric', 'Before APEX', 'After APEX'),
        ('Applications per Day', '3-4', '50+'),
        ('Processing Time', '2-4 hours', '45 seconds'),
        ('Error Rate', '8-12%', '<1%'),
        ('Underwriter Focus', 'All applications', 'Complex cases only'),
    ]
    for i, row_data in enumerate(impact_data):
        for j, cell_data in enumerate(row_data):
            impact_table.rows[i].cells[j].text = cell_data
            if i == 0:
                impact_table.rows[i].cells[j].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_heading('Technical Reality', level=3)
    tech_points = [
        'Zero code written',
        'Data never leaves your AWS account',
        'Full audit trail for compliance',
        'Scale up or down instantly',
        'Works with existing systems via Actions',
    ]
    for point in tech_points:
        doc.add_paragraph(f'✓ {point}')

    doc.add_page_break()

    # Q&A Section
    doc.add_heading('Anticipated Q&A', level=1)

    qa_pairs = [
        ('Q: "What AI models are you using?"',
         'A: "We use Amazon Bedrock - Claude and Amazon Nova models. The architecture also supports '
         'fine-tuned models on your own data for even higher accuracy."'),

        ('Q: "How accurate is the data extraction?"',
         'A: "Out of the box, 90-95% on standard forms. With fine-tuning on your specific '
         'application formats, we\'ve seen 98%+ accuracy."'),

        ('Q: "What about PII security?"',
         'A: "All processing happens inside your AWS VPC. We don\'t see your data - APEX is the '
         'orchestration layer, not the data layer. You maintain full control and compliance."'),

        ('Q: "Can it integrate with our policy admin system?"',
         'A: "Yes - through our Actions module. We have pre-built connectors for Guidewire, '
         'Duck Creek, Majesco, and can build custom integrations to any API."'),

        ('Q: "What\'s the ROI?"',
         'A: "Typical customers see 70-80% reduction in processing costs, 90% faster turnaround, '
         'and improved accuracy. ROI is typically achieved within 6 months."'),
    ]

    for q, a in qa_pairs:
        p = doc.add_paragraph()
        p.add_run(q).bold = True
        doc.add_paragraph(a)
        doc.add_paragraph()

    doc.add_page_break()

    # Appendix
    doc.add_heading('Technical Appendix', level=1)

    doc.add_heading('URLs', level=2)
    urls = [
        ('Frontend:', 'http://localhost:3000'),
        ('Backend API:', 'http://localhost:8000'),
        ('API Documentation:', 'http://localhost:8000/docs'),
    ]
    for label, url in urls:
        p = doc.add_paragraph()
        p.add_run(f'{label} ').bold = True
        p.add_run(url)

    doc.add_heading('Emergency Troubleshooting', level=2)
    troubleshooting = [
        ('Agent doesn\'t respond:', 'Check AgentCore status in AWS Console'),
        ('Extraction fails:', 'Verify blueprint is saved correctly'),
        ('Frontend crashes:', 'Restart with npm run dev'),
        ('Backend errors:', 'Check terminal for Python exceptions'),
    ]
    for issue, solution in troubleshooting:
        p = doc.add_paragraph()
        p.add_run(f'{issue} ').bold = True
        p.add_run(solution)

    doc.add_heading('Post-Demo Follow-Up', level=2)
    followup = [
        'Send recording to attendees',
        'Share this script as leave-behind',
        'Schedule technical deep-dive for interested parties',
        'Provide sandbox access for hands-on evaluation',
    ]
    for item in followup:
        doc.add_paragraph(f'☐ {item}')

    # Save document
    output_path = '/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/docs/APEX_Demo_Script_Insurance_Underwriting.docx'
    doc.save(output_path)
    print(f'Document saved to: {output_path}')
    return output_path

if __name__ == '__main__':
    create_demo_document()
