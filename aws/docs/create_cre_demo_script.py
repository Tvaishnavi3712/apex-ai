"""
Generate APEX Demo Script Word Document - Commercial Real Estate Underwriting
Complete end-to-end workflow: Blueprint → Playbook → Actions → Agent → Deploy → Test → Monitor
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_shading(cell, color):
    """Set cell background color."""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)

def create_demo_script():
    doc = Document()

    # ========== COVER PAGE ==========
    doc.add_paragraph()
    doc.add_paragraph()

    title = doc.add_heading('APEX AI Platform', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph('Live Demo Script')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].bold = True
    subtitle.runs[0].font.size = Pt(24)

    doc.add_paragraph()

    demo_title = doc.add_paragraph('Commercial Real Estate Underwriting')
    demo_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    demo_title.runs[0].font.size = Pt(18)
    demo_title.runs[0].font.color.rgb = RGBColor(0, 51, 102)

    tagline = doc.add_paragraph('"From Document Submission to Underwriting Decision in Minutes"')
    tagline.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tagline.runs[0].italic = True
    tagline.runs[0].font.size = Pt(14)

    doc.add_paragraph()
    doc.add_paragraph()

    # Demo info table
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ('Duration:', '20-25 Minutes'),
        ('Audience:', 'Insurance Executives, Underwriting Leaders'),
        ('Use Case:', 'Commercial Property Insurance'),
        ('Demo Date:', 'March 2026'),
    ]
    for i, (label, value) in enumerate(info_data):
        info_table.rows[i].cells[0].text = label
        info_table.rows[i].cells[1].text = value
        info_table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_page_break()

    # ========== EXECUTIVE SUMMARY ==========
    doc.add_heading('EXECUTIVE SUMMARY', level=1)

    obj = doc.add_paragraph()
    obj.add_run('Demo Objective: ').bold = True
    obj.add_run('Demonstrate how APEX AI Platform enables insurance companies to build, deploy, and monitor AI-powered underwriting agents - transforming manual document review into automated risk assessment without writing code.')

    doc.add_paragraph()

    doc.add_heading('The Problem We\'re Solving', level=2)
    problem = doc.add_paragraph()
    problem.add_run('Commercial real estate underwriting is document-intensive and time-consuming:\n\n')
    problem.add_run('• ')
    problem.add_run('50+ page submission packages').bold = True
    problem.add_run(' with property details, financials, loss history\n')
    problem.add_run('• ')
    problem.add_run('2-3 hours per submission').bold = True
    problem.add_run(' for manual review and data extraction\n')
    problem.add_run('• ')
    problem.add_run('Inconsistent decisions').bold = True
    problem.add_run(' across underwriters and regions\n')
    problem.add_run('• ')
    problem.add_run('Bottlenecks at quarter-end').bold = True
    problem.add_run(' when submission volume spikes')

    doc.add_paragraph()

    doc.add_heading('The APEX Solution', level=2)
    solution = doc.add_paragraph()
    solution.add_run('An AI underwriting agent that:\n\n')
    solution.add_run('• Extracts all key data from submission documents in ')
    solution.add_run('under 30 seconds\n').bold = True
    solution.add_run('• Applies your underwriting guidelines ')
    solution.add_run('consistently\n').bold = True
    solution.add_run('• Routes decisions: Auto-approve, Refer, or Decline based on ')
    solution.add_run('your rules\n').bold = True
    solution.add_run('• Provides ')
    solution.add_run('full audit trail').bold = True
    solution.add_run(' for compliance')

    doc.add_paragraph()

    # Value Props Box
    doc.add_heading('Key Value Propositions', level=2)
    vp_table = doc.add_table(rows=4, cols=2)
    vp_table.style = 'Table Grid'
    vp_data = [
        ('1. Your Infrastructure', 'All data stays in your AWS account - critical for insurance compliance'),
        ('2. No Code Required', 'Business users define underwriting logic in plain English'),
        ('3. Production Ready', 'Built-in testing, guardrails, and monitoring from day one'),
        ('4. Enterprise Scale', 'Process hundreds of submissions per day with consistent quality'),
    ]
    for i, (title, desc) in enumerate(vp_data):
        vp_table.rows[i].cells[0].text = title
        vp_table.rows[i].cells[1].text = desc
        vp_table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_page_break()

    # ========== PRE-DEMO CHECKLIST ==========
    doc.add_heading('PRE-DEMO CHECKLIST', level=1)

    checklist = [
        'Frontend running at http://localhost:3000',
        'Backend running at http://localhost:8000',
        'Sample CRE submission PDFs ready in /synthetic-data/insurance/',
        'Browser tabs open: Dashboard, Canvas, Agents, Agent Hub, Command Center',
        'Demo data cleared (fresh start for live demo)',
        'AWS Console open (optional - to show AgentCore deployment)',
    ]
    for item in checklist:
        doc.add_paragraph(f'☐ {item}')

    doc.add_paragraph()

    # Demo flow overview
    doc.add_heading('Demo Flow Overview', level=2)
    flow_table = doc.add_table(rows=10, cols=3)
    flow_table.style = 'Table Grid'
    flow_headers = ['Act', 'Duration', 'What Happens']
    for i, header in enumerate(flow_headers):
        flow_table.rows[0].cells[i].text = header
        flow_table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
        set_cell_shading(flow_table.rows[0].cells[i], '003366')
        flow_table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    flow_data = [
        ('1. The Problem', '2 min', 'Set the stage - underwriting challenges'),
        ('2. Dashboard Tour', '1 min', 'Overview of APEX platform'),
        ('3. Create Blueprint', '4 min', 'Define CRE submission document structure'),
        ('4. Create Playbook', '4 min', 'Define underwriting workflow & rules'),
        ('5. Configure Actions', '2 min', 'Set up tools the agent can use'),
        ('6. Create Agent', '2 min', 'Bring it all together'),
        ('7. Deploy Agent', '2 min', 'Deploy to AWS Bedrock AgentCore'),
        ('8. Test Agent', '3 min', 'Process sample submissions'),
        ('9. Monitor & Metrics', '2 min', 'Command Center overview'),
    ]
    for i, (act, duration, desc) in enumerate(flow_data, 1):
        flow_table.rows[i].cells[0].text = act
        flow_table.rows[i].cells[1].text = duration
        flow_table.rows[i].cells[2].text = desc

    doc.add_page_break()

    # ========== ACT 1: THE PROBLEM ==========
    doc.add_heading('ACT 1: The Problem (2 minutes)', level=1)

    talking = doc.add_paragraph()
    talking.add_run('[TALKING POINT - No Screen Yet]\n').bold = True

    say1 = doc.add_paragraph()
    say1.add_run('SAY:\n').bold = True
    say1.add_run('"Let me paint a picture of what commercial underwriting looks like today.\n\n')
    say1.add_run('Meet Jennifer, a senior underwriter at a regional P&C carrier. Her inbox has 15 new CRE submissions this morning - office buildings, retail centers, industrial warehouses.\n\n')
    say1.add_run('For each one, she needs to:\n')
    say1.add_run('1. Review the 30-50 page submission package\n')
    say1.add_run('2. Extract property details - construction, occupancy, values\n')
    say1.add_run('3. Analyze loss history and claims patterns\n')
    say1.add_run('4. Check flood zones, crime rates, building codes\n')
    say1.add_run('5. Review tenant schedules and financials\n')
    say1.add_run('6. Make a decision: quote, decline, or refer to senior UW\n\n')
    say1.add_run('Each submission takes 2-3 hours. Jennifer can realistically handle 4-5 per day. The backlog grows every week, and brokers are getting frustrated with turnaround times."\n')

    pause = doc.add_paragraph()
    pause.add_run('[PAUSE]\n').bold = True

    say1b = doc.add_paragraph()
    say1b.add_run('SAY:\n').bold = True
    say1b.add_run('"What if Jennifer had an AI agent that could handle the data extraction and initial triage automatically?\n\n')
    say1b.add_run('An agent that reads every submission, applies your underwriting guidelines consistently, and only brings Jennifer the ones that need her expertise?\n\n')
    say1b.add_run('Let\'s build that agent right now - in the next 20 minutes."')

    doc.add_page_break()

    # ========== ACT 2: DASHBOARD TOUR ==========
    doc.add_heading('ACT 2: The APEX Dashboard (1 minute)', level=1)

    nav = doc.add_paragraph()
    nav.add_run('[Navigate to: http://localhost:3000]\n').bold = True

    say2 = doc.add_paragraph()
    say2.add_run('SAY:\n').bold = True
    say2.add_run('"This is APEX AI Platform - your command center for building and managing AI agents.\n\n')
    say2.add_run('Let me walk you through the main areas:"\n')

    tour = doc.add_paragraph()
    tour.add_run('[Point to each menu item as you describe it]\n\n').bold = True
    tour.add_run('• ')
    tour.add_run('Canvas').bold = True
    tour.add_run(' - Where we design our AI workflows. Think of it as the design studio.\n\n')
    tour.add_run('• ')
    tour.add_run('Agents').bold = True
    tour.add_run(' - Our deployed AI workers. Each agent has a specific job.\n\n')
    tour.add_run('• ')
    tour.add_run('Actions').bold = True
    tour.add_run(' - The tools our agents can use. Database lookups, API calls, notifications.\n\n')
    tour.add_run('• ')
    tour.add_run('Agent Hub').bold = True
    tour.add_run(' - Where humans interact with agents. Chat interface, work queues.\n\n')
    tour.add_run('• ')
    tour.add_run('Command Center').bold = True
    tour.add_run(' - Real-time monitoring. Processing metrics, success rates, alerts.\n')

    say2b = doc.add_paragraph()
    say2b.add_run('SAY:\n').bold = True
    say2b.add_run('"Let\'s start building. First, we need to teach APEX what a CRE submission looks like."')

    doc.add_page_break()

    # ========== ACT 3: CREATE BLUEPRINT ==========
    doc.add_heading('ACT 3: Create the Blueprint (4 minutes)', level=1)

    nav3 = doc.add_paragraph()
    nav3.add_run('[Navigate to: Canvas → Blueprints tab → Click "New Blueprint"]\n').bold = True

    say3 = doc.add_paragraph()
    say3.add_run('SAY:\n').bold = True
    say3.add_run('"A Blueprint is how we teach the AI to understand a document type. We\'re telling it: here\'s what a CRE submission looks like, and here\'s what data to extract."\n')

    doc.add_heading('Step 1: Basic Information', level=2)
    step1 = doc.add_paragraph()
    step1.add_run('[Fill in these fields live - type slowly so audience can follow]\n\n').bold = True

    fields1 = doc.add_table(rows=4, cols=2)
    fields1.style = 'Table Grid'
    fields1_data = [
        ('Blueprint Name:', 'CRE Underwriting Submission'),
        ('Industry:', 'Insurance Underwriting'),
        ('Document Type:', 'Underwriting Submission'),
        ('Description:', 'Extract key underwriting data from commercial real estate insurance submission packages'),
    ]
    for i, (label, value) in enumerate(fields1_data):
        fields1.rows[i].cells[0].text = label
        fields1.rows[i].cells[1].text = value
        fields1.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()

    doc.add_heading('Step 2: Define Extraction Fields', level=2)

    say3_intro = doc.add_paragraph()
    say3_intro.add_run('SAY:\n').bold = True
    say3_intro.add_run('"Now we need to define what data to extract. APEX gives you TWO options:"\n')

    doc.add_paragraph()

    # ===== OPTION A: IMPORT DOCUMENT =====
    doc.add_heading('OPTION A: Import Document (RECOMMENDED for Demo)', level=3)

    option_a = doc.add_paragraph()
    option_a.add_run('[This is the faster, more impressive approach for demos]\n\n').bold = True

    say_option_a = doc.add_paragraph()
    say_option_a.add_run('SAY:\n').bold = True
    say_option_a.add_run('"Instead of defining fields manually, let me show you something powerful. I\'ll upload a sample document and let the AI figure out the schema automatically."\n')

    step_import = doc.add_paragraph()
    step_import.add_run('[Click "Generate from Sample" button with the sparkle icon]\n\n').bold = True
    step_import.add_run('[A modal appears - click "Upload Document" or drag & drop]\n\n').bold = True
    step_import.add_run('[Upload: submission_01_office_good_risk.pdf]\n\n').bold = True

    say_import = doc.add_paragraph()
    say_import.add_run('SAY:\n').bold = True
    say_import.add_run('"Watch what happens. The AI is analyzing this 6-page submission package..."\n\n')
    say_import.add_run('[Wait 5-10 seconds for AI to analyze]\n\n').bold = True

    say_import2 = doc.add_paragraph()
    say_import2.add_run('SAY:\n').bold = True
    say_import2.add_run('"Look at that - it automatically identified 15+ fields:\n')
    say_import2.add_run('• Submission ID, Insured Name, Property Address\n')
    say_import2.add_run('• Building details - year built, square footage, construction type\n')
    say_import2.add_run('• Financial data - TIV, occupancy rate, DSCR\n')
    say_import2.add_run('• Risk factors - flood zone, sprinkler status\n')
    say_import2.add_run('• Loss history as an array\n\n')
    say_import2.add_run('The AI read the document and understood its structure. No manual field definition required."\n')

    step_accept = doc.add_paragraph()
    step_accept.add_run('[Review the suggested fields, then click "Accept Schema"]\n\n').bold = True

    say_accept = doc.add_paragraph()
    say_accept.add_run('SAY:\n').bold = True
    say_accept.add_run('"I can accept all fields, or pick and choose. Let me accept these and we\'re done with the Blueprint in under a minute."\n')

    doc.add_paragraph()

    # Divider
    divider = doc.add_paragraph()
    divider.add_run('─' * 50).bold = True
    divider.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    # ===== OPTION B: MANUAL ENTRY =====
    doc.add_heading('OPTION B: Manual Field Entry (Alternative)', level=3)

    option_b = doc.add_paragraph()
    option_b.add_run('[Use this approach if you want to show fine-grained control]\n\n').bold = True

    say3b = doc.add_paragraph()
    say3b.add_run('SAY:\n').bold = True
    say3b.add_run('"Alternatively, you can define fields manually for complete control. Let me show you:"\n')

    step2 = doc.add_paragraph()
    step2.add_run('[Click "Add Field" and add these one by one - type the descriptions]\n\n').bold = True

    fields_table = doc.add_table(rows=16, cols=4)
    fields_table.style = 'Table Grid'
    field_headers = ['Field Name', 'Type', 'Required', 'Description']
    for i, h in enumerate(field_headers):
        fields_table.rows[0].cells[i].text = h
        fields_table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
        set_cell_shading(fields_table.rows[0].cells[i], '003366')
        fields_table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    fields_data = [
        ('submission_id', 'string', 'Yes', 'Unique submission reference number'),
        ('insured_name', 'string', 'Yes', 'Legal name of the insured entity'),
        ('property_address', 'string', 'Yes', 'Full street address of the property'),
        ('property_type', 'string', 'Yes', 'Type: Office, Retail, Industrial, Mixed-Use'),
        ('year_built', 'number', 'Yes', 'Year the building was constructed'),
        ('square_footage', 'number', 'Yes', 'Total building square footage'),
        ('construction_type', 'string', 'Yes', 'ISO construction class (1-6)'),
        ('total_insured_value', 'number', 'Yes', 'Total insurable value (TIV) in dollars'),
        ('occupancy_rate', 'number', 'No', 'Current occupancy percentage'),
        ('sprinklered', 'boolean', 'Yes', 'Does property have sprinkler system?'),
        ('flood_zone', 'string', 'Yes', 'FEMA flood zone designation'),
        ('prior_losses', 'array', 'No', 'List of losses in past 5 years with amounts'),
        ('total_loss_amount', 'number', 'No', 'Sum of all prior losses'),
        ('debt_service_coverage', 'number', 'No', 'DSCR ratio from financials'),
        ('broker_name', 'string', 'Yes', 'Submitting broker name'),
    ]
    for i, (name, ftype, req, desc) in enumerate(fields_data, 1):
        fields_table.rows[i].cells[0].text = name
        fields_table.rows[i].cells[1].text = ftype
        fields_table.rows[i].cells[2].text = req
        fields_table.rows[i].cells[3].text = desc

    doc.add_paragraph()

    step3 = doc.add_paragraph()
    step3.add_run('[Click "Save Blueprint"]\n\n').bold = True

    say3c = doc.add_paragraph()
    say3c.add_run('SAY:\n').bold = True
    say3c.add_run('"That\'s it. APEX now understands CRE submissions. This blueprint will use Amazon Bedrock Data Automation to extract these fields from any format - typed, scanned, or handwritten.\n\n')
    say3c.add_run('Notice what we didn\'t do: no ML training, no labeled datasets, no Python code. Just plain English descriptions."')

    doc.add_page_break()

    # ========== ACT 4: CREATE PLAYBOOK ==========
    doc.add_heading('ACT 4: Create the Playbook (4 minutes)', level=1)

    nav4 = doc.add_paragraph()
    nav4.add_run('[Navigate to: Canvas → Playbooks tab → Click "New Playbook"]\n').bold = True

    say4 = doc.add_paragraph()
    say4.add_run('SAY:\n').bold = True
    say4.add_run('"Now we define what the agent should DO with the extracted data. A Playbook is the agent\'s instructions - written in plain English, just like you\'d train a new underwriter."\n')

    doc.add_heading('Step 1: Playbook Details', level=2)
    pb_table = doc.add_table(rows=4, cols=2)
    pb_table.style = 'Table Grid'
    pb_data = [
        ('Playbook Name:', 'CRE Underwriting Workflow'),
        ('Industry:', 'Insurance Underwriting'),
        ('Blueprint:', 'CRE Underwriting Submission'),
        ('Description:', 'Automated underwriting workflow for commercial real estate submissions'),
    ]
    for i, (label, value) in enumerate(pb_data):
        pb_table.rows[i].cells[0].text = label
        pb_table.rows[i].cells[1].text = value
        pb_table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()

    doc.add_heading('Step 2: Define Intent', level=2)
    say4b = doc.add_paragraph()
    say4b.add_run('[Type this in the Intent field]\n\n').bold = True

    intent_box = doc.add_paragraph()
    intent_box.add_run('Process incoming commercial real estate insurance submissions by extracting key property and financial data, assessing risk factors against underwriting guidelines, and routing to the appropriate decision path: auto-approve for clean risks, refer to underwriter for moderate complexity, or decline for submissions outside appetite.').italic = True

    doc.add_paragraph()

    doc.add_heading('Step 3: Define Business Rules', level=2)
    say4c = doc.add_paragraph()
    say4c.add_run('SAY:\n').bold = True
    say4c.add_run('"These are your underwriting guidelines - the rules Jennifer follows every day."\n\n')
    say4c.add_run('[Type these rules]\n').bold = True

    rules = doc.add_paragraph()
    rules.add_run('''
APPROVAL THRESHOLDS:
• TIV under $25M with no losses: Auto-Approve eligible
• TIV $25M-$75M: Standard review
• TIV over $75M: Senior underwriter referral required

AUTOMATIC DECLINE TRIGGERS:
• Flood Zone A or V (high-risk coastal)
• Loss ratio exceeding 75% in past 5 years
• DSCR below 1.10 (financial distress)
• Building age over 50 years without recent renovation

REFERRAL TRIGGERS:
• Any prior loss over $500,000
• Occupancy below 70%
• Mixed-use with residential component
• Construction type ISO Class 1-2 (frame)
''')

    doc.add_paragraph()

    doc.add_heading('Step 4: Define the Recipe (Workflow Steps)', level=2)
    say4d = doc.add_paragraph()
    say4d.add_run('[Type this recipe - the step-by-step workflow]\n').bold = True

    recipe = doc.add_paragraph()
    recipe.add_run('''
## Step 1: Extract Submission Data
Use the CRE Underwriting Submission blueprint to extract all fields from the submitted documents. Validate that required fields are present.

## Step 2: Risk Assessment - Property
Evaluate property-level risk factors:
- Check construction type against our appetite
- Verify sprinkler and fire protection status
- Assess building age and condition
- Check flood zone and natural hazard exposure

## Step 3: Risk Assessment - Financial
Evaluate financial stability:
- Calculate debt service coverage ratio
- Check occupancy rate against minimums
- Review tenant quality if available

## Step 4: Loss History Analysis
Review prior claims:
- Calculate 5-year loss ratio
- Identify any large losses over $100K
- Flag frequency patterns

## Step 5: Apply Underwriting Decision
Based on all factors:
- If all green flags and TIV < $25M: APPROVE with standard terms
- If any yellow flags or TIV $25M-$75M: REFER to underwriter with summary
- If any red flags (decline triggers): DECLINE with reason code

## Step 6: Generate Output
Create structured response with:
- Decision (Approve/Refer/Decline)
- Risk score (1-100)
- Key factors summary
- Recommended premium range (if approved)
- Required conditions or exclusions
''')

    step_save = doc.add_paragraph()
    step_save.add_run('[Click "Save Playbook"]\n').bold = True

    say4e = doc.add_paragraph()
    say4e.add_run('SAY:\n').bold = True
    say4e.add_run('"Look at what we just created - a complete underwriting workflow in plain English. These are the same rules Jennifer uses, just written down for the AI to follow consistently, every time, on every submission."')

    doc.add_page_break()

    # ========== ACT 5: CONFIGURE ACTIONS ==========
    doc.add_heading('ACT 5: Configure Actions (2 minutes)', level=1)

    nav5 = doc.add_paragraph()
    nav5.add_run('[Navigate to: Actions]\n').bold = True

    say5 = doc.add_paragraph()
    say5.add_run('SAY:\n').bold = True
    say5.add_run('"Actions are the tools our agent can use. Think of them as the agent\'s hands - how it interacts with your systems and data."\n\n')
    say5.add_run('[Show the Actions list]\n').bold = True

    say5b = doc.add_paragraph()
    say5b.add_run('SAY:\n').bold = True
    say5b.add_run('"APEX comes with pre-built actions for common operations. Let me show you what\'s available for underwriting:"\n')

    actions_table = doc.add_table(rows=7, cols=3)
    actions_table.style = 'Table Grid'
    actions_headers = ['Action', 'Category', 'What It Does']
    for i, h in enumerate(actions_headers):
        actions_table.rows[0].cells[i].text = h
        actions_table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
        set_cell_shading(actions_table.rows[0].cells[i], '003366')
        actions_table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    actions_data = [
        ('extract_document', 'Core', 'Uses BDA to extract data from uploaded documents'),
        ('lookup_flood_zone', 'Insurance', 'Checks FEMA flood zone by property address'),
        ('check_loss_history', 'Insurance', 'Queries loss database for prior claims'),
        ('calculate_premium', 'Insurance', 'Runs rating algorithm for premium indication'),
        ('route_to_underwriter', 'Workflow', 'Creates work item for human review'),
        ('send_notification', 'Core', 'Sends email/SMS notifications'),
    ]
    for i, (action, cat, desc) in enumerate(actions_data, 1):
        actions_table.rows[i].cells[0].text = action
        actions_table.rows[i].cells[1].text = cat
        actions_table.rows[i].cells[2].text = desc

    doc.add_paragraph()

    say5c = doc.add_paragraph()
    say5c.add_run('SAY:\n').bold = True
    say5c.add_run('"Each action is a Lambda function that runs in your AWS account. You can use our pre-built actions or create custom ones that integrate with your existing systems - your policy admin, your rating engine, your CRM.\n\n')
    say5c.add_run('The agent automatically knows when to use each action based on the playbook steps."')

    doc.add_page_break()

    # ========== ACT 6: CREATE AGENT ==========
    doc.add_heading('ACT 6: Create the Agent (2 minutes)', level=1)

    nav6 = doc.add_paragraph()
    nav6.add_run('[Navigate to: Agents → Click "Create Agent"]\n').bold = True

    say6 = doc.add_paragraph()
    say6.add_run('SAY:\n').bold = True
    say6.add_run('"Now we bring everything together. An Agent combines the Blueprint, Playbook, and Actions into a working AI worker."\n')

    doc.add_heading('Configure the Agent', level=2)
    agent_table = doc.add_table(rows=6, cols=2)
    agent_table.style = 'Table Grid'
    agent_data = [
        ('Agent Name:', 'UnderwriteBot'),
        ('Description:', 'AI underwriting assistant for commercial real estate submissions'),
        ('Playbook:', 'CRE Underwriting Workflow'),
        ('Model:', 'Amazon Nova Pro'),
        ('Runtime:', 'AWS Bedrock AgentCore'),
        ('Status:', 'Development'),
    ]
    for i, (label, value) in enumerate(agent_data):
        agent_table.rows[i].cells[0].text = label
        agent_table.rows[i].cells[1].text = value
        agent_table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()

    say6b = doc.add_paragraph()
    say6b.add_run('[Click "Create"]\n\n').bold = True
    say6b.add_run('SAY:\n').bold = True
    say6b.add_run('"The agent is created. Notice the Runtime setting - AWS Bedrock AgentCore. This is critical:\n\n')
    say6b.add_run('• Your data never leaves your AWS account\n')
    say6b.add_run('• Full SOC 2 and regulatory compliance\n')
    say6b.add_run('• You control the model, the data, the access\n\n')
    say6b.add_run('For insurance, this is non-negotiable. Your submission data, your underwriting rules - they stay in YOUR infrastructure."')

    doc.add_page_break()

    # ========== ACT 7: DEPLOY AGENT ==========
    doc.add_heading('ACT 7: Deploy the Agent (2 minutes)', level=1)

    nav7 = doc.add_paragraph()
    nav7.add_run('[On the Agent detail page → Click "Deploy"]\n').bold = True

    say7 = doc.add_paragraph()
    say7.add_run('SAY:\n').bold = True
    say7.add_run('"Let\'s deploy UnderwriteBot to production."\n\n')
    say7.add_run('[Click Deploy button]\n\n').bold = True
    say7.add_run('"Behind the scenes, APEX is:\n')
    say7.add_run('1. Packaging the agent code and configuration\n')
    say7.add_run('2. Building a container image\n')
    say7.add_run('3. Deploying to AWS Bedrock AgentCore\n')
    say7.add_run('4. Setting up the API endpoint\n\n')
    say7.add_run('This typically takes 30-60 seconds."')

    doc.add_paragraph()

    wait = doc.add_paragraph()
    wait.add_run('[Wait for deployment to complete - status changes to "Active"]\n').bold = True

    say7b = doc.add_paragraph()
    say7b.add_run('SAY:\n').bold = True
    say7b.add_run('"And we\'re live. UnderwriteBot is now deployed and ready to process submissions.\n\n')
    say7b.add_run('Let me point out what we DIDN\'T do:\n')
    say7b.add_run('• No code written\n')
    say7b.add_run('• No infrastructure provisioned manually\n')
    say7b.add_run('• No ML model training\n')
    say7b.add_run('• No DevOps pipelines configured\n\n')
    say7b.add_run('We described what we wanted in plain English, and APEX handled the rest."')

    doc.add_page_break()

    # ========== ACT 8: TEST AGENT ==========
    doc.add_heading('ACT 8: Test the Agent (3 minutes)', level=1)

    nav8 = doc.add_paragraph()
    nav8.add_run('[Navigate to: Agent Hub → Select UnderwriteBot]\n').bold = True

    say8 = doc.add_paragraph()
    say8.add_run('SAY:\n').bold = True
    say8.add_run('"Let\'s test UnderwriteBot with real submissions. I have three test cases that represent different risk profiles."\n')

    doc.add_heading('Test Case 1: Good Risk (Auto-Approve)', level=2)
    test1 = doc.add_paragraph()
    test1.add_run('[Upload: submission_01_office_good_risk.pdf]\n\n').bold = True
    test1.add_run('Or type:\n').bold = True

    prompt1 = doc.add_paragraph()
    prompt1.add_run('''
Process this CRE submission:
- Submission ID: CRE-2024-00142
- Insured: Meridian Office Partners LLC
- Property: 500 California Street, San Francisco
- Type: Class A Office Building
- Year Built: 2008
- Square Feet: 125,000
- TIV: $27,000,000
- Construction: Fire Resistive (ISO Class 6)
- Sprinklered: Yes - Full NFPA 13
- Flood Zone: X (minimal risk)
- Occupancy: 96%
- DSCR: 1.85
- Loss History: None in past 5 years
''').italic = True

    wait1 = doc.add_paragraph()
    wait1.add_run('[Wait for response]\n\n').bold = True

    say8b = doc.add_paragraph()
    say8b.add_run('SAY:\n').bold = True
    say8b.add_run('"Watch what the agent does:\n')
    say8b.add_run('1. Extracts all the key data points\n')
    say8b.add_run('2. Checks construction, sprinklers, flood zone - all green\n')
    say8b.add_run('3. Reviews financials - strong DSCR, high occupancy\n')
    say8b.add_run('4. No loss history - clean\n')
    say8b.add_run('5. TIV within appetite\n\n')
    say8b.add_run('[Read the response]\n\n').bold = True
    say8b.add_run('The agent APPROVED this submission because all factors align with our underwriting guidelines. This took 15 seconds instead of 2 hours."')

    doc.add_paragraph()

    doc.add_heading('Test Case 2: Moderate Risk (Refer to Underwriter)', level=2)
    test2 = doc.add_paragraph()
    test2.add_run('[Upload: submission_02_mixed_use_moderate_risk.pdf]\n\n').bold = True
    test2.add_run('Or type:\n').bold = True

    prompt2 = doc.add_paragraph()
    prompt2.add_run('''
Process this CRE submission:
- Submission ID: CRE-2024-00187
- Insured: Bayshore Mixed-Use Development LLC
- Property: 1500 Bayshore Drive, Miami
- Type: Mixed-Use (Retail/Office/Residential)
- Year Built: 2019
- Square Feet: 285,000
- TIV: $54,000,000
- Construction: Fire Resistive
- Sprinklered: Yes
- Flood Zone: AE (HIGH RISK)
- Occupancy: 88%
- DSCR: 1.31
- Loss History: $185,000 (Hurricane Ian 2022), $45,000 (water damage 2023)
''').italic = True

    wait2 = doc.add_paragraph()
    wait2.add_run('[Wait for response]\n\n').bold = True

    say8c = doc.add_paragraph()
    say8c.add_run('SAY:\n').bold = True
    say8c.add_run('"This one is different. The agent REFERRED this to an underwriter because:\n')
    say8c.add_run('• Flood Zone AE - high-risk coastal exposure\n')
    say8c.add_run('• Prior hurricane loss - $185K from Ian\n')
    say8c.add_run('• Mixed-use with residential - triggers referral per our guidelines\n')
    say8c.add_run('• Lower DSCR (1.31) - tighter financials\n\n')
    say8c.add_run('The AI isn\'t replacing Jennifer - it\'s triaging. Clean risks get approved automatically. Complex risks go to Jennifer with a full summary so she can make an informed decision quickly."')

    doc.add_paragraph()

    doc.add_heading('Test Case 3: High Risk (Decline)', level=2)
    test3 = doc.add_paragraph()
    test3.add_run('[Upload: submission_03_industrial_high_risk.pdf]\n\n').bold = True
    test3.add_run('Or summarize:\n').bold = True

    prompt3 = doc.add_paragraph()
    prompt3.add_run('''
This is an industrial warehouse in Houston:
- Flood Zone A, near Ship Channel
- 4 losses totaling $1.58M in 4 years
- Building B is unsprinklered with code violations
- DSCR of 1.04 - financial distress
- 67% occupancy
- Prior non-renewals from two carriers
''').italic = True

    say8d = doc.add_paragraph()
    say8d.add_run('[Wait for response]\n\n').bold = True
    say8d.add_run('SAY:\n').bold = True
    say8d.add_run('"This submission was DECLINED. Multiple red flags:\n')
    say8d.add_run('• Significant loss history - over $1.5M in claims\n')
    say8d.add_run('• Flood Zone A - outside our appetite\n')
    say8d.add_run('• Unsprinklered with code violations\n')
    say8d.add_run('• DSCR of 1.04 - barely covering debt\n\n')
    say8d.add_run('The agent followed our guidelines exactly. This would have been a clear decline from Jennifer too - but now she doesn\'t have to spend time on it."')

    doc.add_page_break()

    # ========== ACT 9: MONITOR & METRICS ==========
    doc.add_heading('ACT 9: Monitor & Metrics (2 minutes)', level=1)

    nav9 = doc.add_paragraph()
    nav9.add_run('[Navigate to: Command Center]\n').bold = True

    say9 = doc.add_paragraph()
    say9.add_run('SAY:\n').bold = True
    say9.add_run('"The Command Center is your real-time window into agent performance."\n\n')
    say9.add_run('[Point to key metrics as you describe them]\n').bold = True

    metrics = doc.add_paragraph()
    metrics.add_run('\n• ')
    metrics.add_run('Documents Processed').bold = True
    metrics.add_run(' - Total submissions handled today/week/month\n\n')
    metrics.add_run('• ')
    metrics.add_run('Decision Distribution').bold = True
    metrics.add_run(' - Approved vs Referred vs Declined breakdown\n\n')
    metrics.add_run('• ')
    metrics.add_run('Average Processing Time').bold = True
    metrics.add_run(' - Typically under 30 seconds per submission\n\n')
    metrics.add_run('• ')
    metrics.add_run('Success Rate').bold = True
    metrics.add_run(' - Percentage processed without errors\n\n')
    metrics.add_run('• ')
    metrics.add_run('Active Agents').bold = True
    metrics.add_run(' - Status of all deployed agents\n')

    say9b = doc.add_paragraph()
    say9b.add_run('[Show the Activity Feed]\n\n').bold = True
    say9b.add_run('SAY:\n').bold = True
    say9b.add_run('"This live feed shows every submission being processed. Green for approved, yellow for referred, red for declined.\n\n')
    say9b.add_run('Every decision is logged with full audit trail - what data was extracted, what rules were applied, why the decision was made. Critical for compliance and regulatory review."\n')

    say9c = doc.add_paragraph()
    say9c.add_run('[Point to alerts section]\n\n').bold = True
    say9c.add_run('SAY:\n').bold = True
    say9c.add_run('"If anything goes wrong - extraction errors, API timeouts, unusual patterns - you see it here immediately. Proactive monitoring, not reactive firefighting."')

    doc.add_page_break()

    # ========== VALUE PROPOSITION ==========
    doc.add_heading('ACT 10: The Value Proposition (2 minutes)', level=1)

    nav10 = doc.add_paragraph()
    nav10.add_run('[Return to Dashboard or show summary slide]\n').bold = True

    say10 = doc.add_paragraph()
    say10.add_run('SAY:\n').bold = True
    say10.add_run('"Let\'s recap what we built in the last 20 minutes:\n\n')

    recap = doc.add_table(rows=7, cols=2)
    recap.style = 'Table Grid'
    recap_data = [
        ('Step', 'What We Did'),
        ('1. Blueprint', 'Taught AI to understand CRE submissions'),
        ('2. Playbook', 'Defined underwriting rules in plain English'),
        ('3. Actions', 'Connected to rating, loss history, notifications'),
        ('4. Agent', 'Combined everything into UnderwriteBot'),
        ('5. Deploy', 'Launched to AWS Bedrock AgentCore'),
        ('6. Test', 'Processed 3 submissions with accurate decisions'),
    ]
    for i, (step, desc) in enumerate(recap_data):
        recap.rows[i].cells[0].text = step
        recap.rows[i].cells[1].text = desc
        if i == 0:
            recap.rows[i].cells[0].paragraphs[0].runs[0].bold = True
            recap.rows[i].cells[1].paragraphs[0].runs[0].bold = True
            set_cell_shading(recap.rows[i].cells[0], '003366')
            set_cell_shading(recap.rows[i].cells[1], '003366')
            recap.rows[i].cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            recap.rows[i].cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    doc.add_paragraph()

    say10b = doc.add_paragraph()
    say10b.add_run('SAY:\n').bold = True
    say10b.add_run('"')
    say10b.add_run('The Business Impact:\n').bold = True
    say10b.add_run('• Jennifer now processes 50+ submissions per day instead of 4-5\n')
    say10b.add_run('• Average handling time: 2 hours → 30 seconds\n')
    say10b.add_run('• Consistent application of underwriting guidelines - every time\n')
    say10b.add_run('• Broker turnaround time: days → hours\n')
    say10b.add_run('• Full audit trail for compliance\n\n')
    say10b.add_run('The Technical Reality:\n').bold = True
    say10b.add_run('• Zero code written\n')
    say10b.add_run('• Data never left your AWS account\n')
    say10b.add_run('• Deployed in under an hour, not months\n')
    say10b.add_run('• Scale up instantly for quarter-end volume"')

    doc.add_page_break()

    # ========== Q&A ==========
    doc.add_heading('Q&A - Anticipated Questions', level=1)

    qa_items = [
        ('Q: "What AI models are you using?"',
         'A: "We use Amazon Bedrock - specifically Amazon Nova and Claude models. The platform supports any Bedrock model, and you can even bring your own fine-tuned models."'),

        ('Q: "How accurate is the data extraction?"',
         'A: "Out of the box, 92-95% on standard submission formats. With fine-tuning on your specific broker templates, we\'ve seen 98%+ accuracy. The Blueprint approach lets you continuously improve extraction quality."'),

        ('Q: "What about regulatory compliance?"',
         'A: "All processing happens in your AWS VPC. Full audit trail for every decision. You control the data, the rules, the access. We\'ve designed this for regulated industries from day one."'),

        ('Q: "Can it integrate with our policy admin system?"',
         'A: "Yes - through our Actions module. We have pre-built connectors and can build custom integrations to any API. Common integrations include Guidewire, Duck Creek, Majesco."'),

        ('Q: "What happens when the AI makes a mistake?"',
         'A: "The referral workflow is designed exactly for this. Any uncertainty routes to human review. You set the confidence thresholds. Jennifer always has the final say on complex risks."'),

        ('Q: "How long does implementation take?"',
         'A: "Pilot in 4-6 weeks. Full production in 60-90 days. The demo you just saw - we can replicate that for your submission types in a matter of days."'),
    ]

    for q, a in qa_items:
        qa_p = doc.add_paragraph()
        qa_p.add_run(q + '\n').bold = True
        qa_p.add_run(a)
        doc.add_paragraph()

    doc.add_page_break()

    # ========== TECHNICAL APPENDIX ==========
    doc.add_heading('TECHNICAL APPENDIX', level=1)

    doc.add_heading('Environment URLs', level=2)
    urls = doc.add_paragraph()
    urls.add_run('• Frontend: http://localhost:3000\n')
    urls.add_run('• Backend API: http://localhost:8000\n')
    urls.add_run('• API Docs: http://localhost:8000/docs\n')
    urls.add_run('• AWS Console: Bedrock AgentCore\n')

    doc.add_heading('Test Data Location', level=2)
    test_loc = doc.add_paragraph()
    test_loc.add_run('/synthetic-data/insurance/commercial_real_estate/\n')
    test_loc.add_run('• submission_01_office_good_risk.pdf\n')
    test_loc.add_run('• submission_02_mixed_use_moderate_risk.pdf\n')
    test_loc.add_run('• submission_03_industrial_high_risk.pdf\n')

    doc.add_heading('Emergency Troubleshooting', level=2)
    trouble = doc.add_paragraph()
    trouble.add_run('• Agent not responding: ').bold = True
    trouble.add_run('Check AgentCore status in AWS Console\n')
    trouble.add_run('• Extraction fails: ').bold = True
    trouble.add_run('Verify Blueprint is saved and deployed\n')
    trouble.add_run('• Frontend crashes: ').bold = True
    trouble.add_run('Restart with npm run dev\n')
    trouble.add_run('• Backend errors: ').bold = True
    trouble.add_run('Check uvicorn logs, restart if needed\n')

    doc.add_paragraph()
    doc.add_paragraph()

    # Footer
    footer = doc.add_paragraph()
    footer.add_run('─' * 60)
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    footer2 = doc.add_paragraph()
    footer2.add_run('Document Version: 1.0 | Last Updated: March 2026 | APEX AI Platform Team')
    footer2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer2.runs[0].font.color.rgb = RGBColor(128, 128, 128)

    # Save
    output_path = '/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/docs/APEX_Demo_Script_CRE_Underwriting.docx'
    doc.save(output_path)
    print(f"Demo script saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_demo_script()
