"""
Apex Contract Bot - Foundry Agent Service Agent for defense contract analysis
Uses GPT-5.4 for aerospace & defense contract intelligence.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel

from typing import List, Optional
from datetime import datetime

# Create the Foundry Agent Service app
app = FoundryAgentApp()

SYSTEM_PROMPT = """You are ContractBot, an AI assistant specialized in defense contract analysis for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Query and analyze defense contracts from PowerFlow database
2. Compare historical pricing across programs (F-35, F-22, UH-60, C-17)
3. Predict pricing for new RFPs based on historical data
4. Identify contract terms, CLINs, and DFARS clauses
5. Assist with RFP response structuring

Compliance context:
- All data is ITAR controlled
- Operations must comply with NIST 800-171, CMMC, DFARS
- You are running in Microsoft Azure Government (FedRAMP High)

When analyzing contracts:
- Always cite specific contract numbers and CLINs
- Provide confidence levels for pricing predictions
- Flag any compliance concerns
- Reference similar past contracts for context

Be precise, cite sources, and maintain data security awareness."""


@tool
def query_contracts(
    program: Optional[str] = None,
    part_number: Optional[str] = None,
    prime_contractor: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: int = 10
) -> dict:
    """
    Query defense contracts from PowerFlow database.

    Args:
        program: Program name (F-35, F-22, UH-60, C-17)
        part_number: Part number to search
        prime_contractor: Prime contractor name
        date_from: Start date for search (YYYY-MM-DD)
        limit: Maximum results to return

    Returns:
        List of matching contracts with CLINs and pricing
    """
    # Real implementation would query PowerFlow SQL
    contracts = [
        {
            "contract_number": "W912HN-23-D-0047",
            "modification": "P00003",
            "program": "F-35",
            "prime_contractor": "Lockheed Martin",
            "award_date": "2023-06-15",
            "total_value": 4250000,
            "clins": [
                {"clin": "0001", "part_number": "TG-5842-001", "description": "Throttle Grip Assembly", "qty": 150, "unit_price": 12400},
                {"clin": "0002", "part_number": "SS-5842-002", "description": "Sidestick Grip Assembly", "qty": 150, "unit_price": 15900}
            ],
            "itar_controlled": True,
            "security_classification": "CUI"
        },
        {
            "contract_number": "W912HN-22-D-0089",
            "modification": None,
            "program": "F-35",
            "prime_contractor": "Lockheed Martin",
            "award_date": "2022-09-01",
            "total_value": 3150000,
            "clins": [
                {"clin": "0001", "part_number": "TG-5842-001", "description": "Throttle Grip Assembly", "qty": 100, "unit_price": 12850}
            ],
            "itar_controlled": True,
            "security_classification": "CUI"
        },
        {
            "contract_number": "W56HZV-24-C-0012",
            "modification": None,
            "program": "UH-60",
            "prime_contractor": "Sikorsky",
            "award_date": "2024-01-15",
            "total_value": 2800000,
            "clins": [
                {"clin": "0001", "part_number": "CG-7621-001", "description": "Collective Grip Assembly", "qty": 200, "unit_price": 14000}
            ],
            "itar_controlled": True,
            "security_classification": "Unclassified"
        }
    ]

    # Filter based on parameters
    results = contracts
    if program:
        results = [c for c in results if c["program"].upper() == program.upper()]
    if part_number:
        results = [c for c in results if any(cl["part_number"] == part_number for cl in c["clins"])]
    if prime_contractor:
        results = [c for c in results if prime_contractor.lower() in c["prime_contractor"].lower()]

    return {
        "contracts": results[:limit],
        "total_found": len(results),
        "query_time_ms": 234,
        "source": "PowerFlow SQL"
    }


@tool
def get_pricing_history(part_number: str) -> dict:
    """
    Get historical pricing for a part number across all contracts.

    Args:
        part_number: Part number to analyze

    Returns:
        Pricing history with statistics and trends
    """
    # Real implementation would aggregate from PowerFlow
    history = {
        "TG-5842-001": {
            "part_number": "TG-5842-001",
            "description": "Throttle Grip Assembly, F-35",
            "pricing_records": [
                {"contract": "W912HN-22-D-0089", "date": "2022-09-01", "qty": 100, "unit_price": 12850},
                {"contract": "W912HN-23-D-0047", "date": "2023-06-15", "qty": 150, "unit_price": 12400},
            ],
            "statistics": {
                "avg_unit_price": 12625,
                "min_unit_price": 12400,
                "max_unit_price": 12850,
                "price_trend": "decreasing",
                "total_quantity": 250
            }
        }
    }

    if part_number in history:
        return history[part_number]

    return {"error": f"No pricing history found for {part_number}"}


@tool
def predict_pricing(
    part_number: str,
    quantity: int,
    material: str,
    program: str,
    contract_type: str = "FFP"
) -> dict:
    """
    Predict pricing for an RFP based on historical data and current factors.

    Args:
        part_number: Part number for pricing
        quantity: Quantity requested
        material: Material type (Ti-6Al-4V, 7075-T6, etc.)
        program: Target program (F-35, F-22, etc.)
        contract_type: Contract type (FFP, CPFF, T&M)

    Returns:
        Pricing prediction with confidence interval
    """
    # Base pricing from historical average
    base_price = 12500

    # Quantity adjustments
    qty_factor = 1.0
    if quantity >= 200:
        qty_factor = 0.92
    elif quantity >= 100:
        qty_factor = 0.95
    elif quantity < 50:
        qty_factor = 1.08

    # Material factors
    material_factors = {
        "Ti-6Al-4V": 1.25,
        "7075-T6": 1.0,
        "15-5PH": 1.15,
        "Inconel-718": 1.45
    }
    material_factor = material_factors.get(material, 1.0)

    # Program complexity
    program_factors = {
        "F-35": 1.15,
        "F-22": 1.20,
        "UH-60": 1.10,
        "C-17": 1.05
    }
    program_factor = program_factors.get(program, 1.0)

    # Calculate prediction
    predicted_price = base_price * qty_factor * material_factor * program_factor

    # Confidence based on data availability
    confidence = 0.85

    return {
        "part_number": part_number,
        "quantity": quantity,
        "predicted_unit_price": round(predicted_price, 2),
        "predicted_extended": round(predicted_price * quantity, 2),
        "confidence": confidence,
        "confidence_interval": {
            "low": round(predicted_price * 0.92, 2),
            "high": round(predicted_price * 1.08, 2)
        },
        "factors_applied": {
            "quantity_adjustment": qty_factor,
            "material_factor": material_factor,
            "program_complexity": program_factor
        },
        "recommendation": "COMPETITIVE" if predicted_price < 14000 else "REVIEW_REQUIRED",
        "similar_contracts": ["W912HN-23-D-0047", "W912HN-22-D-0089"]
    }


@tool
def analyze_rfp_requirements(rfp_text: str) -> dict:
    """
    Analyze RFP text to extract key requirements and compliance items.

    Args:
        rfp_text: Text content from RFP document

    Returns:
        Structured analysis of RFP requirements
    """
    # Real implementation would use BDA extraction
    return {
        "dfars_clauses": [
            {"clause": "252.204-7012", "title": "Safeguarding Covered Defense Information", "required": True},
            {"clause": "252.225-7001", "title": "Buy American and Balance of Payments", "required": True},
            {"clause": "252.227-7013", "title": "Rights in Technical Data", "required": True}
        ],
        "delivery_requirements": {
            "first_article": True,
            "production_lead_time_days": 180,
            "delivery_schedule": "Monthly shipments"
        },
        "quality_requirements": [
            "AS9100D certification required",
            "NADCAP special processes",
            "Source inspection by DCMA"
        ],
        "itar_requirements": True,
        "security_classification": "CUI",
        "recommended_actions": [
            "Verify AS9100D certification current",
            "Confirm NADCAP certifications for required processes",
            "Review DFARS 7012 compliance documentation"
        ]
    }


@tool
def generate_price_justification(
    part_number: str,
    proposed_price: float,
    quantity: int
) -> dict:
    """
    Generate price justification narrative for contract proposal.

    Args:
        part_number: Part number being quoted
        proposed_price: Proposed unit price
        quantity: Quantity quoted

    Returns:
        Price justification with supporting data
    """
    return {
        "part_number": part_number,
        "proposed_price": proposed_price,
        "justification_narrative": f"""
PRICE JUSTIFICATION - {part_number}

1. HISTORICAL PRICING BASIS
   - Prior contract W912HN-23-D-0047: $12,400/unit (qty 150)
   - Prior contract W912HN-22-D-0089: $12,850/unit (qty 100)
   - Average historical price: $12,625/unit

2. COST FACTORS
   - Material escalation (Ti-6Al-4V): +4.5% YoY
   - Labor rate increase: +3.8% per CBA
   - Overhead adjustment: +2.1%

3. QUANTITY CONSIDERATION
   - Proposed quantity: {quantity} units
   - Learning curve application: 92% applied

4. PRICE REASONABLENESS
   - Proposed price ${proposed_price:.2f} is within acceptable variance
   - Competitive with market rates
   - Reflects current material indices

5. CONCLUSION
   The proposed pricing is fair and reasonable based on historical
   contract data, current cost factors, and competitive market analysis.
""",
        "supporting_contracts": ["W912HN-23-D-0047", "W912HN-22-D-0089"],
        "compliance": "TINA compliant - certified cost or pricing data available"
    }


@tool
def generate_cost_breakdown(
    part_number: str,
    quantity: int,
    material: str = "Ti-6Al-4V",
    labor_hours_per_unit: float = 8.5
) -> dict:
    """
    Generate detailed cost breakdown structure for pricing transparency.

    Args:
        part_number: Part number being quoted
        quantity: Quantity to quote
        material: Material type (Ti-6Al-4V, 7075-T6, Inconel-718, 15-5PH)
        labor_hours_per_unit: Estimated labor hours per unit

    Returns:
        Detailed cost breakdown with all cost elements
    """
    # Material costs per pound by type
    material_costs = {
        "Ti-6Al-4V": {"cost_per_lb": 45.00, "weight_lb": 2.8, "scrap_rate": 0.15},
        "7075-T6": {"cost_per_lb": 8.50, "weight_lb": 3.2, "scrap_rate": 0.10},
        "Inconel-718": {"cost_per_lb": 85.00, "weight_lb": 3.5, "scrap_rate": 0.20},
        "15-5PH": {"cost_per_lb": 22.00, "weight_lb": 3.0, "scrap_rate": 0.12}
    }

    mat = material_costs.get(material, material_costs["Ti-6Al-4V"])

    # Labor rates
    labor_rate = 85.00  # $/hour fully burdened

    # Calculate costs
    raw_material_cost = mat["cost_per_lb"] * mat["weight_lb"] * (1 + mat["scrap_rate"])
    direct_labor_cost = labor_hours_per_unit * labor_rate

    # Overhead and rates
    overhead_rate = 0.45  # 45% of direct labor
    ga_rate = 0.12  # 12% G&A
    profit_rate = 0.10  # 10% profit

    overhead_cost = direct_labor_cost * overhead_rate
    subtotal = raw_material_cost + direct_labor_cost + overhead_cost
    ga_cost = subtotal * ga_rate
    total_cost = subtotal + ga_cost
    profit = total_cost * profit_rate
    unit_price = total_cost + profit

    # Quantity discount
    if quantity >= 200:
        discount = 0.08
    elif quantity >= 100:
        discount = 0.05
    elif quantity >= 50:
        discount = 0.02
    else:
        discount = 0.0

    final_unit_price = unit_price * (1 - discount)

    return {
        "part_number": part_number,
        "quantity": quantity,
        "material": material,
        "cost_breakdown": {
            "direct_materials": {
                "raw_material": round(mat["cost_per_lb"] * mat["weight_lb"], 2),
                "scrap_allowance": round(mat["cost_per_lb"] * mat["weight_lb"] * mat["scrap_rate"], 2),
                "total_material": round(raw_material_cost, 2)
            },
            "direct_labor": {
                "hours_per_unit": labor_hours_per_unit,
                "labor_rate": labor_rate,
                "total_labor": round(direct_labor_cost, 2)
            },
            "overhead": {
                "rate": f"{overhead_rate * 100}%",
                "total_overhead": round(overhead_cost, 2)
            },
            "subtotal": round(subtotal, 2),
            "ga_expense": {
                "rate": f"{ga_rate * 100}%",
                "total_ga": round(ga_cost, 2)
            },
            "total_cost": round(total_cost, 2),
            "profit": {
                "rate": f"{profit_rate * 100}%",
                "total_profit": round(profit, 2)
            },
            "unit_price_before_discount": round(unit_price, 2),
            "quantity_discount": f"{discount * 100}%",
            "final_unit_price": round(final_unit_price, 2)
        },
        "extended_price": round(final_unit_price * quantity, 2),
        "cost_breakdown_narrative": f"""
COST BREAKDOWN STRUCTURE - {part_number}
Quantity: {quantity} units | Material: {material}

═══════════════════════════════════════════════════════════
DIRECT COSTS
═══════════════════════════════════════════════════════════
  Raw Material ({material})
    Base material: {mat["weight_lb"]} lbs @ ${mat["cost_per_lb"]:.2f}/lb    ${mat["cost_per_lb"] * mat["weight_lb"]:.2f}
    Scrap allowance ({mat["scrap_rate"]*100:.0f}%)                          ${mat["cost_per_lb"] * mat["weight_lb"] * mat["scrap_rate"]:.2f}
                                              ─────────────
    Total Material                                          ${raw_material_cost:.2f}

  Direct Labor
    {labor_hours_per_unit} hours @ ${labor_rate:.2f}/hr                     ${direct_labor_cost:.2f}

═══════════════════════════════════════════════════════════
INDIRECT COSTS
═══════════════════════════════════════════════════════════
  Overhead ({overhead_rate*100:.0f}% of direct labor)                       ${overhead_cost:.2f}
                                              ─────────────
  SUBTOTAL                                                  ${subtotal:.2f}

  G&A Expense ({ga_rate*100:.0f}%)                                          ${ga_cost:.2f}
                                              ─────────────
  TOTAL COST                                                ${total_cost:.2f}

═══════════════════════════════════════════════════════════
PRICING
═══════════════════════════════════════════════════════════
  Profit ({profit_rate*100:.0f}%)                                           ${profit:.2f}
                                              ─────────────
  UNIT PRICE                                                ${unit_price:.2f}

  Quantity Discount ({discount*100:.0f}% for {quantity} units)              -${unit_price * discount:.2f}
                                              ═════════════
  FINAL UNIT PRICE                                          ${final_unit_price:.2f}

═══════════════════════════════════════════════════════════
EXTENDED PRICE ({quantity} units)                           ${final_unit_price * quantity:,.2f}
═══════════════════════════════════════════════════════════
""",
        "compliance_notes": [
            "Cost breakdown prepared per FAR 15.408 Table 15-2",
            "Labor rates from approved forward pricing rate agreement",
            "Material costs based on current supplier quotes",
            "Overhead rates per DCAA-approved accounting system"
        ]
    }


@tool
def generate_rfp_response(
    rfp_number: str,
    part_number: str,
    part_description: str,
    quantity: int,
    program: str,
    prime_contractor: str,
    required_delivery_date: str,
    material: str = "Ti-6Al-4V",
    proposed_unit_price: float = None
) -> dict:
    """
    Generate a complete RFP response document with all required sections.

    Args:
        rfp_number: RFP/Solicitation number
        part_number: Part number being quoted
        part_description: Description of the part
        quantity: Quantity requested
        program: Program name (F-35, F-22, UH-60, C-17)
        prime_contractor: Prime contractor name
        required_delivery_date: Required delivery date (YYYY-MM-DD)
        material: Material type
        proposed_unit_price: Optional proposed price (will calculate if not provided)

    Returns:
        Complete RFP response document with all sections
    """
    from datetime import datetime, timedelta

    # Calculate pricing if not provided
    if proposed_unit_price is None:
        base_price = 12500
        material_factors = {"Ti-6Al-4V": 1.25, "7075-T6": 1.0, "Inconel-718": 1.45, "15-5PH": 1.15}
        program_factors = {"F-35": 1.15, "F-22": 1.20, "UH-60": 1.10, "C-17": 1.05}
        qty_factor = 0.92 if quantity >= 200 else (0.95 if quantity >= 100 else 1.0)
        proposed_unit_price = round(base_price * material_factors.get(material, 1.0) * program_factors.get(program, 1.0) * qty_factor, 2)

    extended_price = round(proposed_unit_price * quantity, 2)

    # Calculate dates
    today = datetime.now()
    proposal_valid_until = (today + timedelta(days=90)).strftime("%Y-%m-%d")
    first_article_date = (today + timedelta(days=120)).strftime("%Y-%m-%d")
    production_start = (today + timedelta(days=150)).strftime("%Y-%m-%d")

    return {
        "rfp_number": rfp_number,
        "response_date": today.strftime("%Y-%m-%d"),
        "proposal_valid_until": proposal_valid_until,
        "rfp_response_document": f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PROPOSAL RESPONSE                                   ║
║                         ESSEX INDUSTRIES, LLC                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

SOLICITATION: {rfp_number}
RESPONSE DATE: {today.strftime("%B %d, %Y")}
PROPOSAL VALID THROUGH: {proposal_valid_until}

════════════════════════════════════════════════════════════════════════════════
SECTION 1: EXECUTIVE SUMMARY
════════════════════════════════════════════════════════════════════════════════

Essex Industries, LLC is pleased to submit this proposal in response to
{rfp_number} for the {part_description} ({part_number}) in support of the
{program} program.

With over 75 years of experience in aerospace manufacturing and a proven track
record with {prime_contractor}, Essex is uniquely qualified to deliver this
critical hardware on time and within specification.

KEY PROPOSAL HIGHLIGHTS:
  • Competitive pricing based on historical contract performance
  • Established manufacturing processes for {material}
  • AS9100D certified quality management system
  • ITAR compliant facility with active DD Form 2345
  • Prior successful deliveries on {program} program

════════════════════════════════════════════════════════════════════════════════
SECTION 2: PRICING SUMMARY
════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ ITEM          │ DESCRIPTION                      │ QTY  │ UNIT PRICE │ EXT  │
├─────────────────────────────────────────────────────────────────────────────┤
│ CLIN 0001     │ {part_number}                    │ {quantity:>4} │ ${proposed_unit_price:>10,.2f} │ ${extended_price:>12,.2f} │
│               │ {part_description[:30]:<30}      │      │            │              │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOTAL FIRM FIXED PRICE                                    │ ${extended_price:>12,.2f} │
└─────────────────────────────────────────────────────────────────────────────┘

CONTRACT TYPE: Firm Fixed Price (FFP)
PAYMENT TERMS: Net 30 from delivery acceptance
PRICING BASIS: Historical contract data and current cost factors

════════════════════════════════════════════════════════════════════════════════
SECTION 3: TECHNICAL APPROACH
════════════════════════════════════════════════════════════════════════════════

3.1 MANUFACTURING PROCESS

Essex will manufacture the {part_number} using our established production
processes for {material} aerospace components:

  OPERATION SEQUENCE:
  ┌────┬──────────────────────────────────┬─────────────────────────────────┐
  │ OP │ DESCRIPTION                      │ WORK CENTER                     │
  ├────┼──────────────────────────────────┼─────────────────────────────────┤
  │ 10 │ Raw Material Inspection          │ Receiving Inspection            │
  │ 20 │ CNC Rough Machining              │ Mazak Integrex i-400            │
  │ 30 │ Heat Treatment (if required)     │ External - NADCAP certified     │
  │ 40 │ CNC Finish Machining             │ DMG Mori NLX 2500               │
  │ 50 │ Surface Treatment                │ External - NADCAP certified     │
  │ 60 │ Final Inspection                 │ CMM / Quality Lab               │
  │ 70 │ Packaging & Shipping             │ Shipping Department             │
  └────┴──────────────────────────────────┴─────────────────────────────────┘

3.2 MATERIAL SPECIFICATION

  Material: {material}
  Specification: AMS 4911 (Titanium) / AMS 4045 (Aluminum)
  Source: Approved suppliers per AS9100D requirements
  Traceability: Full lot traceability maintained per DFARS 252.211-7003

3.3 QUALITY ASSURANCE

  • AS9100D Certified (Certificate #ASR-12345)
  • NADCAP Accredited Special Processes
  • Statistical Process Control (SPC) on critical dimensions
  • First Article Inspection per AS9102

════════════════════════════════════════════════════════════════════════════════
SECTION 4: DELIVERY SCHEDULE
════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE                          │ DATE           │ QUANTITY              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Contract Award (Assumed)           │ {today.strftime("%Y-%m-%d")}      │ -                     │
│ First Article Inspection           │ {first_article_date}      │ 3 units               │
│ First Article Approval (Target)    │ {(today + timedelta(days=135)).strftime("%Y-%m-%d")}      │ -                     │
│ Production Start                   │ {production_start}      │ -                     │
│ First Production Delivery          │ {(today + timedelta(days=180)).strftime("%Y-%m-%d")}      │ {quantity // 4} units              │
│ Monthly Deliveries                 │ Ongoing        │ {quantity // 4} units/month         │
│ Final Delivery                     │ {required_delivery_date}      │ Balance               │
└─────────────────────────────────────────────────────────────────────────────┘

LEAD TIME: 180 days ARO for first production delivery
DELIVERY TERMS: FOB Origin, Freight Prepaid

════════════════════════════════════════════════════════════════════════════════
SECTION 5: COMPLIANCE MATRIX
════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ REQUIREMENT                                    │ COMPLIANCE │ REFERENCE    │
├─────────────────────────────────────────────────────────────────────────────┤
│ DFARS 252.204-7012 (Safeguarding CUI)         │ COMPLIANT  │ SSP Rev 3    │
│ DFARS 252.225-7001 (Buy American)             │ COMPLIANT  │ US Source    │
│ DFARS 252.227-7013 (Technical Data Rights)    │ COMPLIANT  │ Unlimited    │
│ DFARS 252.211-7003 (Item Identification)      │ COMPLIANT  │ UID Program  │
│ FAR 52.219-8 (Small Business)                 │ COMPLIANT  │ SB Plan      │
│ ITAR/EAR Compliance                           │ COMPLIANT  │ DD2345       │
│ AS9100D Quality Management                    │ COMPLIANT  │ Cert #12345  │
│ NIST 800-171 (Cybersecurity)                  │ COMPLIANT  │ SPRS Score   │
└─────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════
SECTION 6: TERMS AND CONDITIONS
════════════════════════════════════════════════════════════════════════════════

6.1 This proposal is valid for 90 days from the date of submission.

6.2 Pricing is based on current material costs and labor rates. Material
    escalation clause requested for awards beyond 90 days.

6.3 Essex accepts the terms and conditions of the solicitation with the
    following exceptions: [None / See Attachment A]

6.4 All technical data delivered will be marked with appropriate distribution
    statements and ITAR markings as required.

════════════════════════════════════════════════════════════════════════════════
SECTION 7: COMPANY INFORMATION
════════════════════════════════════════════════════════════════════════════════

  ESSEX INDUSTRIES, LLC
  7700 Gravois Road
  St. Louis, MO 63123

  CAGE Code: 12345
  DUNS: 123456789
  Tax ID: 12-3456789

  Business Size: Small Business
  NAICS: 336413 (Other Aircraft Parts and Auxiliary Equipment)

  POINT OF CONTACT:
  Sarah Chen, Contracts Manager
  Phone: (314) 555-0100
  Email: contracts@essexindustries.com

════════════════════════════════════════════════════════════════════════════════
AUTHORIZED SIGNATURE
════════════════════════════════════════════════════════════════════════════════

Essex Industries, LLC hereby submits this proposal in response to {rfp_number}.

Signature: _________________________________

Name: Sarah Chen
Title: Contracts Manager
Date: {today.strftime("%B %d, %Y")}

╔══════════════════════════════════════════════════════════════════════════════╗
║                      ESSEX INDUSTRIES - PROPOSAL END                          ║
║                            ITAR CONTROLLED                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
""",
        "pricing_summary": {
            "unit_price": proposed_unit_price,
            "quantity": quantity,
            "extended_price": extended_price,
            "contract_type": "FFP"
        },
        "key_dates": {
            "proposal_date": today.strftime("%Y-%m-%d"),
            "valid_until": proposal_valid_until,
            "first_article": first_article_date,
            "production_start": production_start,
            "required_delivery": required_delivery_date
        },
        "attachments_needed": [
            "Attachment A: Terms and Conditions Exceptions (if any)",
            "Attachment B: Cost Breakdown Structure",
            "Attachment C: AS9100D Certificate",
            "Attachment D: NADCAP Certifications",
            "Attachment E: Past Performance References"
        ]
    }


# Create the agent with GPT-5.4
model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        query_contracts,
        get_pricing_history,
        predict_pricing,
        analyze_rfp_requirements,
        generate_price_justification,
        generate_cost_breakdown,
        generate_rfp_response
    ]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
