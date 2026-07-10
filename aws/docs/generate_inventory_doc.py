"""
Generate Professional Word Document for Apex AI Platform Inventory
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime


def set_cell_shading(cell, color):
    """Set cell background color"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)


def create_styled_table(doc, headers, rows, header_color="1B4F72", alt_row_color="EBF5FB"):
    """Create a professionally styled table"""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].runs[0].bold = True
        header_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        header_cells[i].paragraphs[0].runs[0].font.size = Pt(11)
        header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(header_cells[i], header_color)

    # Data rows
    for idx, row_data in enumerate(rows):
        row = table.add_row()
        for i, cell_data in enumerate(row_data):
            row.cells[i].text = str(cell_data)
            row.cells[i].paragraphs[0].runs[0].font.size = Pt(10)
            if idx % 2 == 1:
                set_cell_shading(row.cells[i], alt_row_color)

    return table


def add_section_header(doc, text, level=1):
    """Add a styled section header"""
    if level == 1:
        heading = doc.add_heading(text, level=1)
        heading.runs[0].font.color.rgb = RGBColor(27, 79, 114)
        heading.runs[0].font.size = Pt(18)
    elif level == 2:
        heading = doc.add_heading(text, level=2)
        heading.runs[0].font.color.rgb = RGBColor(41, 128, 185)
        heading.runs[0].font.size = Pt(14)
    else:
        heading = doc.add_heading(text, level=3)
        heading.runs[0].font.color.rgb = RGBColor(52, 73, 94)
        heading.runs[0].font.size = Pt(12)


def main():
    doc = Document()

    # Set document margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # ========================================
    # COVER PAGE
    # ========================================

    # Add spacing
    for _ in range(3):
        doc.add_paragraph()

    # Company name
    company = doc.add_paragraph()
    company_run = company.add_run("CBTS")
    company_run.bold = True
    company_run.font.size = Pt(16)
    company_run.font.color.rgb = RGBColor(128, 128, 128)
    company.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Title
    title = doc.add_paragraph()
    title_run = title.add_run("APEX AI PLATFORM")
    title_run.bold = True
    title_run.font.size = Pt(36)
    title_run.font.color.rgb = RGBColor(27, 79, 114)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Subtitle
    subtitle = doc.add_paragraph()
    subtitle_run = subtitle.add_run("Complete Platform Inventory & Architecture")
    subtitle_run.font.size = Pt(18)
    subtitle_run.font.color.rgb = RGBColor(52, 73, 94)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    # Horizontal line
    line = doc.add_paragraph()
    line_run = line.add_run("_" * 60)
    line_run.font.color.rgb = RGBColor(41, 128, 185)
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    # Description
    desc = doc.add_paragraph()
    desc_text = "Enterprise Document Intelligence & Workflow Automation Platform"
    desc_run = desc.add_run(desc_text)
    desc_run.font.size = Pt(14)
    desc_run.italic = True
    desc_run.font.color.rgb = RGBColor(127, 140, 141)
    desc.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add spacing
    for _ in range(6):
        doc.add_paragraph()

    # Version info
    version = doc.add_paragraph()
    version.add_run("Version 1.0").bold = True
    version.alignment = WD_ALIGN_PARAGRAPH.CENTER

    date_para = doc.add_paragraph()
    date_para.add_run(datetime.now().strftime("%B %d, %Y"))
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Page break
    doc.add_page_break()

    # ========================================
    # TABLE OF CONTENTS
    # ========================================

    add_section_header(doc, "Table of Contents", 1)

    toc_items = [
        ("1. Executive Summary", 3),
        ("2. Platform Statistics", 3),
        ("3. Blueprints - Document Extraction Schemas", 4),
        ("4. Runbooks - Workflow Automation", 6),
        ("5. Action Handlers - Business Logic", 8),
        ("6. Backend Services - API & Data Layer", 10),
        ("7. Frontend Components - User Interface", 11),
        ("8. Test Suite - Quality Assurance", 12),
        ("9. Synthetic Test Data", 13),
        ("10. Infrastructure - Cloud Deployment", 14),
        ("11. Industry Coverage Matrix", 15),
    ]

    for item, page in toc_items:
        toc_entry = doc.add_paragraph()
        toc_entry.add_run(item)
        toc_entry.add_run("\t" * 8 + str(page))
        toc_entry.paragraph_format.tab_stops.add_tab_stop(Inches(6.5))

    doc.add_page_break()

    # ========================================
    # EXECUTIVE SUMMARY
    # ========================================

    add_section_header(doc, "1. Executive Summary", 1)

    summary = doc.add_paragraph()
    summary_text = """The Apex AI Platform is a comprehensive enterprise automation solution designed to streamline document processing and workflow management across multiple industries. Built on AWS cloud infrastructure, the platform leverages Amazon Bedrock Data Automation (BDA) for intelligent document extraction, combined with configurable runbooks and modular action handlers to deliver end-to-end automation capabilities.

The platform supports 12 distinct industries with pre-built blueprints, runbooks, and action handlers that can be deployed individually or as complete industry packs. This modular architecture enables rapid deployment while maintaining the flexibility to customize solutions for specific business requirements."""
    summary.add_run(summary_text)
    summary.paragraph_format.space_after = Pt(12)

    # Key highlights
    add_section_header(doc, "Key Highlights", 2)

    highlights = [
        "12 Industries Supported with pre-built automation components",
        "34 Document Blueprints for intelligent data extraction",
        "25 Workflow Runbooks for end-to-end process automation",
        "56+ Action Handlers implementing business logic",
        "Full-stack implementation with FastAPI backend and React frontend",
        "Comprehensive test suite with 30+ test files",
        "50+ synthetic test documents for validation"
    ]

    for highlight in highlights:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(highlight)

    doc.add_page_break()

    # ========================================
    # PLATFORM STATISTICS
    # ========================================

    add_section_header(doc, "2. Platform Statistics", 1)

    stats_data = [
        ("Blueprints", "34", "Document extraction schemas (JSON)"),
        ("Runbooks", "25", "Workflow automation recipes (YAML)"),
        ("Action Handlers", "56+", "Industry-specific Lambda functions"),
        ("Backend Files", "21", "FastAPI, models, services"),
        ("Frontend Files", "35", "React/Next.js components"),
        ("Test Files", "30", "Unit, integration, API tests"),
        ("Synthetic Data", "50+", "Test documents"),
        ("Infrastructure", "2", "CloudFormation templates"),
        ("Industries", "12", "Complete vertical coverage"),
        ("Action Packs", "13", "Pre-configured bundles"),
    ]

    doc.add_paragraph()
    create_styled_table(doc, ["Category", "Count", "Description"], stats_data)

    doc.add_paragraph()

    # Total files callout
    total = doc.add_paragraph()
    total.add_run("TOTAL: ~330 FILES").bold = True
    total.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # ========================================
    # BLUEPRINTS
    # ========================================

    add_section_header(doc, "3. Blueprints - Document Extraction Schemas", 1)

    bp_intro = doc.add_paragraph()
    bp_intro.add_run("Blueprints define the extraction schema for different document types using Amazon Bedrock Data Automation (BDA). Each blueprint specifies the fields to extract, validation rules, and output configuration.")

    doc.add_paragraph()

    blueprint_data = [
        ("Financial Services", "5", "invoice, bank_statement, receipt, contract, w9"),
        ("Healthcare Payers", "3", "medical_claim, eob, prior_authorization"),
        ("Healthcare Providers", "3", "patient_intake, referral, discharge_summary"),
        ("Healthcare Clinical", "3", "lab_results, prescription, clinical_notes"),
        ("Manufacturing", "4", "purchase_order, bill_of_lading, packing_slip, quality_inspection"),
        ("HR / Recruitment", "4", "resume, offer_letter, i9_form, w4_form"),
        ("Insurance Underwriting", "2", "insurance_application, risk_assessment"),
        ("Retail", "2", "receipt, return_form"),
        ("CPG", "2", "product_specification, compliance_certificate"),
        ("Contact Center", "2", "call_transcript, case_notes"),
        ("Supply Chain", "2", "demand_forecast, replenishment_order"),
        ("Airlines", "2", "boarding_pass, baggage_claim"),
    ]

    create_styled_table(doc, ["Industry", "Count", "Blueprints"], blueprint_data)

    doc.add_paragraph()

    # Blueprint structure
    add_section_header(doc, "Blueprint Structure", 2)

    structure = doc.add_paragraph()
    structure.add_run("Each blueprint JSON file contains:").bold = True

    bp_components = [
        "blueprintName & blueprintVersion - Unique identifier and version",
        "bdaSchema - Field definitions with types and extraction instructions",
        "definitions - Nested/complex type definitions (e.g., line items)",
        "extractionRules - Date formats, confidence thresholds",
        "validationRules - Business rule expressions",
        "outputConfiguration - Confidence scores, bounding boxes"
    ]

    for comp in bp_components:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(comp)

    doc.add_page_break()

    # ========================================
    # RUNBOOKS
    # ========================================

    add_section_header(doc, "4. Runbooks - Workflow Automation", 1)

    rb_intro = doc.add_paragraph()
    rb_intro.add_run("Runbooks define end-to-end automation workflows using a natural language recipe format. They orchestrate multiple actions, define business rules, specify triggers, and handle routing logic.")

    doc.add_paragraph()

    runbook_data = [
        ("Financial Services", "4", "invoice_processing, payment_processing, vendor_onboarding, expense_approval"),
        ("Healthcare Payers", "2", "claims_processing, prior_authorization"),
        ("Healthcare Providers", "2", "patient_registration, referral_management"),
        ("Healthcare Clinical", "2", "lab_results_processing, prescription_processing"),
        ("Manufacturing", "3", "po_processing, shipment_tracking, quality_control"),
        ("HR / Recruitment", "3", "resume_screening, onboarding_documents, offer_approval"),
        ("Insurance Underwriting", "1", "underwriting_workflow"),
        ("Retail", "1", "returns_processing"),
        ("CPG", "1", "product_compliance"),
        ("Contact Center", "1", "call_quality_analysis"),
        ("Supply Chain", "2", "inventory_optimization, supplier_performance"),
        ("Airlines", "2", "flight_disruption, baggage_reconciliation"),
    ]

    create_styled_table(doc, ["Industry", "Count", "Runbooks"], runbook_data)

    doc.add_paragraph()

    # Runbook structure
    add_section_header(doc, "Runbook Components", 2)

    rb_components = [
        "Intent - Natural language description of workflow purpose",
        "Output - Expected deliverables with schema definitions",
        "Context - Business rules, thresholds, and policies",
        "Data Sources - S3, DynamoDB, and external integrations",
        "Actions - Referenced action handlers to invoke",
        "Recipe - Step-by-step workflow instructions",
        "Triggers - S3 events, API calls, schedules, EDI transactions",
        "Worker Configuration - Queue, concurrency, timeout settings"
    ]

    for comp in rb_components:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(comp)

    doc.add_page_break()

    # ========================================
    # ACTION HANDLERS
    # ========================================

    add_section_header(doc, "5. Action Handlers - Business Logic", 1)

    action_intro = doc.add_paragraph()
    action_intro.add_run("Action handlers implement discrete, reusable business logic as AWS Lambda functions. Each action uses the Apex SDK with decorator-based schema definitions and class-based implementations.")

    doc.add_paragraph()

    action_data = [
        ("Healthcare Payers", "5", "claims_adjudication, eligibility_verify, medical_necessity, payment_calculate, fraud_detection"),
        ("Healthcare Providers", "5", "patient_lookup, insurance_verify, referral_validate, appointment_schedule, ehr_update"),
        ("Healthcare Clinical", "5", "lab_validate, critical_value_alert, drug_interaction, formulary_check, clinical_decision"),
        ("Retail", "5", "receipt_validate, return_policy, fraud_score, inventory_update, refund_process"),
        ("CPG", "5", "ingredient_validate, regulatory_check, label_compliance, nutrition_validate, allergen_check"),
        ("Insurance Underwriting", "5", "risk_score, premium_calculate, coverage_validate, loss_history, auto_decision"),
        ("Contact Center", "5", "sentiment_analyze, compliance_check, quality_score, coaching_recommend, escalation_detect"),
        ("Airlines", "5", "affected_passengers, auto_rebook, hotel_booking, eu261_compensation, baggage_trace"),
        ("Supply Chain", "7", "forecast_analyze, inventory_analyze, eoq_calculate, reorder_point, quality_metrics, delivery_metrics, scorecard_generate"),
        ("Manufacturing", "3", "inventory_lookup, carrier_validation, quality_threshold"),
        ("HR", "3", "job_requirement_match, compensation_validation, background_check"),
        ("Core / Financial", "7", "bda_extract, dynamodb_lookup, s3_operations, notification, vendor_lookup, po_match, approval_route"),
    ]

    create_styled_table(doc, ["Industry", "Count", "Actions"], action_data)

    doc.add_paragraph()

    # SDK Components
    add_section_header(doc, "Apex Action SDK", 2)

    sdk_components = [
        "@apex_action decorator - Defines action schema, inputs, outputs",
        "ApexActionSchema - Action metadata (name, category, industry)",
        "ActionInputSchema - Input parameter definitions with validation",
        "ActionOutputSchema - Output field specifications",
        "ApexActionBase - Class-based implementation pattern",
        "Lambda handler - Serverless entry point function"
    ]

    for comp in sdk_components:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(comp)

    doc.add_page_break()

    # ========================================
    # BACKEND SERVICES
    # ========================================

    add_section_header(doc, "6. Backend Services - API & Data Layer", 1)

    backend_intro = doc.add_paragraph()
    backend_intro.add_run("The backend is built with FastAPI, providing RESTful APIs for all platform operations. It integrates with DynamoDB for data persistence and S3 for document storage.")

    doc.add_paragraph()

    add_section_header(doc, "API Endpoints", 2)

    api_data = [
        ("Agents", "/api/agents", "CRUD operations, status management"),
        ("Blueprints", "/api/blueprints", "CRUD, BDA deployment"),
        ("Runbooks", "/api/runbooks", "CRUD, deploy, test execution"),
        ("Actions", "/api/actions", "Gallery, packs, registry, invoke"),
        ("Work Items", "/api/work-items", "Queue management, status transitions"),
        ("Documents", "/api/documents", "Upload, processing, results"),
        ("Chat", "/api/chat", "Sessions, messages, WebSocket"),
    ]

    create_styled_table(doc, ["Module", "Endpoint", "Capabilities"], api_data)

    doc.add_paragraph()

    add_section_header(doc, "Services", 2)

    services = [
        "DynamoDBService - Table operations, queries, scans, batch operations",
        "S3Service - Upload, download, presigned URLs, JSON operations",
        "ActionRegistry - Action discovery, registration, invocation"
    ]

    for svc in services:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(svc)

    add_section_header(doc, "Models", 2)

    models = ["Agent", "Blueprint", "Runbook", "Action", "WorkItem"]

    model_para = doc.add_paragraph()
    model_para.add_run("Pydantic models for validation: " + ", ".join(models))

    doc.add_page_break()

    # ========================================
    # FRONTEND COMPONENTS
    # ========================================

    add_section_header(doc, "7. Frontend Components - User Interface", 1)

    fe_intro = doc.add_paragraph()
    fe_intro.add_run("The frontend is built with Next.js and React, using TypeScript for type safety. It features a modular component architecture with Zustand for state management.")

    doc.add_paragraph()

    frontend_data = [
        ("Common", "5", "Button, Card, Badge, Modal, Input"),
        ("Layout", "2", "Layout, Sidebar"),
        ("BlueprintDesigner", "7", "Designer, FieldEditor, FieldList, RuleBuilder, Preview"),
        ("RunbookBuilder", "1", "RunbookEditor (tabbed interface)"),
        ("WorkRoom", "2", "AgentChat, WorkQueue"),
        ("ControlRoom", "2", "AgentMonitor, MetricsDashboard"),
        ("Libraries", "2", "API client, Zustand store"),
        ("Pages", "3", "_app, index, workroom"),
    ]

    create_styled_table(doc, ["Category", "Count", "Components"], frontend_data)

    doc.add_paragraph()

    add_section_header(doc, "Key Features", 2)

    features = [
        "Blueprint Designer - Visual schema builder with field management",
        "Runbook Editor - Tabbed interface for workflow configuration",
        "Agent Chat - Real-time conversation with file attachments",
        "Work Queue - Filtered task management with status grouping",
        "Control Room - Agent monitoring and metrics dashboard"
    ]

    for feat in features:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(feat)

    doc.add_page_break()

    # ========================================
    # TEST SUITE
    # ========================================

    add_section_header(doc, "8. Test Suite - Quality Assurance", 1)

    test_intro = doc.add_paragraph()
    test_intro.add_run("Comprehensive test coverage using pytest for backend and Jest for frontend. Tests use moto for AWS mocking and FastAPI TestClient for API testing.")

    doc.add_paragraph()

    test_data = [
        ("Unit - Models", "5", "agent, blueprint, runbook, action, work_item"),
        ("Unit - Services", "2", "dynamodb, s3"),
        ("Unit - Actions", "9", "All industry action handlers"),
        ("API Tests", "4", "blueprints, runbooks, actions, work_items"),
        ("Integration", "3", "blueprints_validation, runbooks_validation, actions_handlers"),
        ("Frontend", "5", "Component tests with Jest/RTL"),
    ]

    create_styled_table(doc, ["Category", "Count", "Coverage"], test_data)

    doc.add_paragraph()

    add_section_header(doc, "Test Commands", 2)

    commands = doc.add_paragraph()
    commands.add_run("Backend: ").bold = True
    commands.add_run("pytest tests/ -v --cov=. --cov-report=html")

    commands2 = doc.add_paragraph()
    commands2.add_run("Frontend: ").bold = True
    commands2.add_run("npm test -- --coverage")

    doc.add_page_break()

    # ========================================
    # SYNTHETIC DATA
    # ========================================

    add_section_header(doc, "9. Synthetic Test Data", 1)

    synth_intro = doc.add_paragraph()
    synth_intro.add_run("Synthetic test documents provide realistic sample data for testing blueprint extraction and action handler logic without using production data.")

    doc.add_paragraph()

    synth_data = [
        ("Financial - Invoices", "10", "Various invoice formats and vendors"),
        ("Financial - Receipts", "15", "Retail transaction receipts"),
        ("Financial - Statements", "4", "Bank statement extractions"),
        ("Healthcare Payers", "3", "Claims, EOBs, prior authorizations"),
        ("Healthcare Providers", "2", "Patient intake, referrals"),
        ("Healthcare Clinical", "2", "Lab results, prescriptions"),
        ("Retail", "2", "Receipts, return forms"),
        ("Airlines", "2", "Boarding passes, baggage claims"),
        ("Supply Chain", "2", "Forecasts, replenishment orders"),
        ("Others", "8", "CPG, insurance, contact center"),
    ]

    create_styled_table(doc, ["Category", "Count", "Description"], synth_data)

    doc.add_page_break()

    # ========================================
    # INFRASTRUCTURE
    # ========================================

    add_section_header(doc, "10. Infrastructure - Cloud Deployment", 1)

    infra_intro = doc.add_paragraph()
    infra_intro.add_run("Infrastructure as Code using AWS CloudFormation/SAM templates for consistent, repeatable deployments.")

    doc.add_paragraph()

    add_section_header(doc, "Core Infrastructure (main.yaml)", 2)

    core_infra = [
        "DynamoDB Tables - Runbooks, Agents, Blueprints, Actions, WorkItems",
        "S3 Buckets - Documents incoming, processed, results",
        "API Gateway - REST API with Lambda integration",
        "IAM Roles - Service execution permissions",
        "CloudWatch - Logging and monitoring"
    ]

    for item in core_infra:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(item)

    add_section_header(doc, "Lambda Actions (lambda-actions.yaml)", 2)

    lambda_infra = [
        "Function definitions for all action handlers",
        "Environment variable configuration",
        "VPC integration settings",
        "Layer dependencies (SDK, common libraries)",
        "Event source mappings"
    ]

    for item in lambda_infra:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(item)

    doc.add_page_break()

    # ========================================
    # INDUSTRY COVERAGE MATRIX
    # ========================================

    add_section_header(doc, "11. Industry Coverage Matrix", 1)

    matrix_intro = doc.add_paragraph()
    matrix_intro.add_run("Complete breakdown of platform components by industry vertical.")

    doc.add_paragraph()

    matrix_data = [
        ("Financial Services", "5", "4", "7", "Yes"),
        ("Healthcare Payers", "3", "2", "5", "Yes"),
        ("Healthcare Providers", "3", "2", "5", "Yes"),
        ("Healthcare Clinical", "3", "2", "5", "Yes"),
        ("Manufacturing", "4", "3", "3", "Yes"),
        ("HR / Recruitment", "4", "3", "3", "Yes"),
        ("Insurance Underwriting", "2", "1", "5", "Yes"),
        ("Retail", "2", "1", "5", "Yes"),
        ("CPG", "2", "1", "5", "Yes"),
        ("Contact Center", "2", "1", "5", "Yes"),
        ("Supply Chain", "2", "2", "7", "Yes"),
        ("Airlines", "2", "2", "5", "Yes"),
    ]

    create_styled_table(doc, ["Industry", "Blueprints", "Runbooks", "Actions", "Tests"], matrix_data)

    doc.add_paragraph()
    doc.add_paragraph()

    # Action Packs
    add_section_header(doc, "Action Packs", 2)

    packs_intro = doc.add_paragraph()
    packs_intro.add_run("Pre-configured action bundles available for one-click deployment:")

    packs = [
        "Core Actions Pack",
        "Financial Services Pack",
        "Healthcare Payers Pack",
        "Healthcare Providers Pack",
        "Healthcare Clinical Pack",
        "Retail Pack",
        "CPG Pack",
        "Insurance Underwriting Pack",
        "Contact Center Pack",
        "Airlines Pack",
        "Supply Chain Pack",
        "Manufacturing Pack",
        "HR Pack"
    ]

    # Create two columns of packs
    for i in range(0, len(packs), 2):
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(packs[i])
        if i + 1 < len(packs):
            p.add_run("    •    " + packs[i + 1])

    doc.add_page_break()

    # ========================================
    # FOOTER / CLOSING
    # ========================================

    # Add spacing
    for _ in range(8):
        doc.add_paragraph()

    # Closing line
    line = doc.add_paragraph()
    line_run = line.add_run("_" * 60)
    line_run.font.color.rgb = RGBColor(41, 128, 185)
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    closing = doc.add_paragraph()
    closing.add_run("CBTS Accelerator Team").bold = True
    closing.alignment = WD_ALIGN_PARAGRAPH.CENTER

    closing2 = doc.add_paragraph()
    closing2.add_run("Apex AI Platform - Enterprise Document Intelligence")
    closing2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    date_closing = doc.add_paragraph()
    date_closing.add_run(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    date_closing.runs[0].font.size = Pt(9)
    date_closing.runs[0].font.color.rgb = RGBColor(127, 140, 141)
    date_closing.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Save document
    output_path = "/Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws/docs/Apex_AI_Platform_Inventory.docx"
    doc.save(output_path)
    print(f"Document saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
