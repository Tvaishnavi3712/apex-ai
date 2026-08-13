"""
Contract Lookup - Small Factory (READ)
Query PowerFlow SQL database for defense contracts.
Demonstrates READ connector capability.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()


def build_contract_query(
    part_numbers: Optional[List[str]] = None,
    programs: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    prime_contractors: Optional[List[str]] = None,
    limit: int = 100
) -> str:
    """Build SQL query for contract search."""

    query = """
    SELECT
        c.ContractNumber,
        c.ModificationNumber,
        c.ContractType,
        c.PrimeContractor,
        c.ProgramName,
        c.AwardDate,
        c.TotalValue,
        c.FundedAmount,
        c.ITARControlled,
        c.SecurityClassification,
        cl.CLINNumber,
        cl.PartNumber,
        cl.Description,
        cl.Quantity,
        cl.UnitPrice,
        cl.ExtendedPrice,
        cl.DeliveryDate
    FROM dbo.Contracts c
    LEFT JOIN dbo.ContractLineItems cl ON c.ContractID = cl.ContractID
    WHERE 1=1
    """

    conditions = []

    if part_numbers:
        part_list = "', '".join(part_numbers)
        conditions.append(f"cl.PartNumber IN ('{part_list}')")

    if programs:
        program_list = "', '".join(programs)
        conditions.append(f"c.ProgramName IN ('{program_list}')")

    if date_from:
        conditions.append(f"c.AwardDate >= '{date_from}'")

    if date_to:
        conditions.append(f"c.AwardDate <= '{date_to}'")

    if prime_contractors:
        prime_list = "', '".join(prime_contractors)
        conditions.append(f"c.PrimeContractor IN ('{prime_list}')")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += f" ORDER BY c.AwardDate DESC LIMIT {limit}"

    return query


def parse_contract_results(rows: List[Dict]) -> List[Dict[str, Any]]:
    """Parse SQL results into structured contract objects."""

    contracts = {}

    for row in rows:
        contract_num = row.get('ContractNumber')

        if contract_num not in contracts:
            contracts[contract_num] = {
                "contract_number": contract_num,
                "modification_number": row.get('ModificationNumber'),
                "contract_type": row.get('ContractType'),
                "prime_contractor": row.get('PrimeContractor'),
                "program_name": row.get('ProgramName'),
                "award_date": str(row.get('AwardDate', '')),
                "total_value": float(row.get('TotalValue', 0)),
                "funded_amount": float(row.get('FundedAmount', 0)),
                "itar_controlled": bool(row.get('ITARControlled', False)),
                "security_classification": row.get('SecurityClassification', 'Unclassified'),
                "clins": []
            }

        # Add CLIN if present
        if row.get('CLINNumber'):
            contracts[contract_num]["clins"].append({
                "clin_number": row.get('CLINNumber'),
                "part_number": row.get('PartNumber'),
                "description": row.get('Description'),
                "quantity": int(row.get('Quantity', 0)),
                "unit_price": float(row.get('UnitPrice', 0)),
                "extended_price": float(row.get('ExtendedPrice', 0)),
                "delivery_date": str(row.get('DeliveryDate', ''))
            })

    return list(contracts.values())


def calculate_pricing_summary(contracts: List[Dict]) -> Dict[str, Any]:
    """Calculate pricing summary from contracts."""

    if not contracts:
        return {"error": "No contracts found"}

    all_clins = []
    for contract in contracts:
        all_clins.extend(contract.get('clins', []))

    if not all_clins:
        return {"error": "No CLINs found"}

    # Group by part number
    part_pricing = {}
    for clin in all_clins:
        part_num = clin.get('part_number')
        if part_num not in part_pricing:
            part_pricing[part_num] = {
                "part_number": part_num,
                "description": clin.get('description'),
                "prices": [],
                "quantities": [],
                "total_quantity": 0,
                "total_value": 0
            }

        part_pricing[part_num]["prices"].append(clin.get('unit_price', 0))
        part_pricing[part_num]["quantities"].append(clin.get('quantity', 0))
        part_pricing[part_num]["total_quantity"] += clin.get('quantity', 0)
        part_pricing[part_num]["total_value"] += clin.get('extended_price', 0)

    # Calculate statistics
    for part_num, data in part_pricing.items():
        prices = data["prices"]
        data["avg_unit_price"] = sum(prices) / len(prices) if prices else 0
        data["min_unit_price"] = min(prices) if prices else 0
        data["max_unit_price"] = max(prices) if prices else 0
        data["price_trend"] = "stable"

        if len(prices) >= 2:
            if prices[-1] > prices[0] * 1.05:
                data["price_trend"] = "increasing"
            elif prices[-1] < prices[0] * 0.95:
                data["price_trend"] = "decreasing"

    return {
        "parts_analyzed": len(part_pricing),
        "total_contracts": len(contracts),
        "pricing_by_part": list(part_pricing.values())
    }


@register_factory("contract_lookup")
async def contract_lookup(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query PowerFlow database for defense contracts.

    This is a READ-ONLY factory that demonstrates connector capability.

    Input:
        query: Natural language query or structured search params
        config.connection_string: Database connection (from context)
        filters:
            part_numbers: List of part numbers to search
            programs: List of programs (F-35, F-22, etc.)
            date_from: Start date for search
            date_to: End date for search
            prime_contractors: List of prime contractors

    Output:
        contracts: List of matching contracts with CLINs
        pricing_summary: Aggregated pricing analysis
        sources: List of source references
        query_metadata: Query execution details
    """
    config = input_data.get('config', {})
    filters = input_data.get('filters', {})
    query_text = input_data.get('query', '')

    # Extract filters from natural language query if provided
    if query_text and not filters:
        # Simple NLP extraction (would use LLM in production)
        filters = {
            "programs": [],
            "part_numbers": [],
            "limit": 100
        }

        # Check for program mentions
        programs = ["F-35", "F-22", "F-15", "F-16", "C-17", "UH-60", "C-130"]
        for prog in programs:
            if prog.lower() in query_text.lower():
                filters["programs"].append(prog)

        # Check for time ranges
        if "last year" in query_text.lower():
            filters["date_from"] = (datetime.now().replace(year=datetime.now().year - 1)).strftime('%Y-%m-%d')
        elif "last 3 years" in query_text.lower():
            filters["date_from"] = (datetime.now().replace(year=datetime.now().year - 3)).strftime('%Y-%m-%d')

    # Build query
    sql_query = build_contract_query(
        part_numbers=filters.get('part_numbers'),
        programs=filters.get('programs'),
        date_from=filters.get('date_from'),
        date_to=filters.get('date_to'),
        prime_contractors=filters.get('prime_contractors'),
        limit=filters.get('limit', 100)
    )

    # In production, execute against actual database
    # For demo, return mock data
    mock_results = [
        {
            "ContractNumber": "W912HN-23-D-0047",
            "ModificationNumber": "P00003",
            "ContractType": "FFP",
            "PrimeContractor": "Lockheed Martin",
            "ProgramName": "F-35",
            "AwardDate": "2023-06-15",
            "TotalValue": 4250000,
            "FundedAmount": 2850000,
            "ITARControlled": True,
            "SecurityClassification": "CUI",
            "CLINNumber": "0001",
            "PartNumber": "TG-5842-001",
            "Description": "Throttle Grip Assembly, F-35",
            "Quantity": 150,
            "UnitPrice": 12400,
            "ExtendedPrice": 1860000,
            "DeliveryDate": "2024-03-15"
        },
        {
            "ContractNumber": "W912HN-23-D-0047",
            "ModificationNumber": "P00003",
            "ContractType": "FFP",
            "PrimeContractor": "Lockheed Martin",
            "ProgramName": "F-35",
            "AwardDate": "2023-06-15",
            "TotalValue": 4250000,
            "FundedAmount": 2850000,
            "ITARControlled": True,
            "SecurityClassification": "CUI",
            "CLINNumber": "0002",
            "PartNumber": "SS-5842-002",
            "Description": "Sidestick Grip Assembly, F-35",
            "Quantity": 150,
            "UnitPrice": 15900,
            "ExtendedPrice": 2385000,
            "DeliveryDate": "2024-03-15"
        },
        {
            "ContractNumber": "W912HN-22-D-0089",
            "ModificationNumber": None,
            "ContractType": "FFP",
            "PrimeContractor": "Lockheed Martin",
            "ProgramName": "F-35",
            "AwardDate": "2022-09-01",
            "TotalValue": 3150000,
            "FundedAmount": 3150000,
            "ITARControlled": True,
            "SecurityClassification": "CUI",
            "CLINNumber": "0001",
            "PartNumber": "TG-5842-001",
            "Description": "Throttle Grip Assembly, F-35",
            "Quantity": 100,
            "UnitPrice": 12850,
            "ExtendedPrice": 1285000,
            "DeliveryDate": "2023-06-30"
        },
        {
            "ContractNumber": "W56HZV-24-C-0012",
            "ModificationNumber": None,
            "ContractType": "FFP",
            "PrimeContractor": "Sikorsky",
            "ProgramName": "UH-60",
            "AwardDate": "2024-01-15",
            "TotalValue": 2800000,
            "FundedAmount": 2800000,
            "ITARControlled": True,
            "SecurityClassification": "Unclassified",
            "CLINNumber": "0001",
            "PartNumber": "CG-7621-001",
            "Description": "Collective Grip Assembly, UH-60M",
            "Quantity": 200,
            "UnitPrice": 14000,
            "ExtendedPrice": 2800000,
            "DeliveryDate": "2024-09-30"
        }
    ]

    # Parse results
    contracts = parse_contract_results(mock_results)

    # Calculate pricing summary
    pricing_summary = calculate_pricing_summary(contracts)

    # Build source references
    sources = [
        {
            "type": "database",
            "name": "PowerFlow",
            "table": "dbo.Contracts, dbo.ContractLineItems",
            "query_time": "0.234s",
            "records_returned": len(mock_results)
        }
    ]

    logger.info(
        "Contract lookup completed",
        contracts_found=len(contracts),
        programs=filters.get('programs', []),
        mode="READ"
    )

    return {
        "contracts": contracts,
        "pricing_summary": pricing_summary,
        "sources": sources,
        "query_metadata": {
            "filters_applied": filters,
            "sql_query": sql_query,
            "execution_time_ms": 234,
            "mode": "READ",
            "connector": "power_flow_sql"
        }
    }
