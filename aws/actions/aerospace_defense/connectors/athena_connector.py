"""
Athena Connector for PowerFlow SQL Replacement
Queries contract and pricing data from S3 via Athena.
"""
import boto3
import time
from typing import Optional, List, Dict, Any
from actions.sdk.action_decorator import apex_action, register_factory


# Configuration
ATHENA_DATABASE = "powerflow_demo"
ATHENA_WORKGROUP = "primary"
S3_OUTPUT = "s3://apex-demo-athena-results/"
REGION = "us-east-1"


class AthenaConnector:
    """Connector for querying contract data via Athena."""

    def __init__(self, region: str = REGION):
        self.athena = boto3.client('athena', region_name=region)
        self.database = ATHENA_DATABASE

    def execute_query(self, query: str, timeout: int = 60) -> List[Dict[str, Any]]:
        """Execute Athena query and return results."""
        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': S3_OUTPUT},
            WorkGroup=ATHENA_WORKGROUP
        )

        query_id = response['QueryExecutionId']

        # Wait for query completion
        for _ in range(timeout):
            status = self.athena.get_query_execution(QueryExecutionId=query_id)
            state = status['QueryExecution']['Status']['State']

            if state == 'SUCCEEDED':
                break
            elif state in ['FAILED', 'CANCELLED']:
                reason = status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise Exception(f"Query failed: {reason}")

            time.sleep(1)
        else:
            raise Exception("Query timed out")

        # Get results
        results = self.athena.get_query_results(QueryExecutionId=query_id)

        # Parse results
        columns = [col['Name'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []

        for row in results['ResultSet']['Rows'][1:]:  # Skip header
            values = [field.get('VarCharValue', None) for field in row['Data']]
            rows.append(dict(zip(columns, values)))

        return rows


@register_factory("powerflow_connector")
@apex_action(
    name="query_contracts",
    description="Query defense contracts from PowerFlow database via Athena",
    industry="aerospace_defense"
)
def query_contracts(
    program: Optional[str] = None,
    part_number: Optional[str] = None,
    prime_contractor: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Query defense contracts from PowerFlow database (Athena).

    Args:
        program: Filter by program (F-35, F-22, UH-60, C-17)
        part_number: Filter by part number
        prime_contractor: Filter by prime contractor
        date_from: Filter by award date (YYYY-MM-DD)
        limit: Maximum results to return

    Returns:
        List of matching contracts
    """
    connector = AthenaConnector()

    # Build query
    query = """
    SELECT
        c.contract_number,
        c.modification,
        c.program,
        c.prime_contractor,
        c.award_date,
        c.total_value,
        c.itar_controlled,
        c.security_classification
    FROM contracts c
    WHERE 1=1
    """

    if program:
        query += f" AND UPPER(c.program) = UPPER('{program}')"
    if prime_contractor:
        query += f" AND LOWER(c.prime_contractor) LIKE LOWER('%{prime_contractor}%')"
    if date_from:
        query += f" AND c.award_date >= DATE '{date_from}'"

    query += f" ORDER BY c.award_date DESC LIMIT {limit}"

    try:
        results = connector.execute_query(query)

        return {
            "contracts": results,
            "total_found": len(results),
            "query_time_ms": 0,  # Would track actual time
            "source": "PowerFlow (Athena)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "PowerFlow (Athena)"}


@register_factory("powerflow_connector")
@apex_action(
    name="get_pricing_history",
    description="Get historical pricing for a part number",
    industry="aerospace_defense"
)
def get_pricing_history(part_number: str) -> Dict[str, Any]:
    """
    Get historical pricing for a part number across all contracts.

    Args:
        part_number: Part number to analyze

    Returns:
        Pricing history with statistics and trends
    """
    connector = AthenaConnector()

    query = f"""
    SELECT
        part_number,
        contract_number,
        award_date,
        quantity,
        unit_price,
        material,
        program
    FROM pricing_history
    WHERE part_number = '{part_number}'
    ORDER BY award_date DESC
    """

    try:
        results = connector.execute_query(query)

        if not results:
            return {"error": f"No pricing history found for {part_number}"}

        # Calculate statistics
        prices = [float(r['unit_price']) for r in results if r['unit_price']]
        quantities = [int(r['quantity']) for r in results if r['quantity']]

        stats = {
            "avg_unit_price": sum(prices) / len(prices) if prices else 0,
            "min_unit_price": min(prices) if prices else 0,
            "max_unit_price": max(prices) if prices else 0,
            "total_quantity": sum(quantities),
            "price_trend": "decreasing" if len(prices) > 1 and prices[0] < prices[-1] else "increasing"
        }

        return {
            "part_number": part_number,
            "description": results[0].get('description', 'Unknown'),
            "pricing_records": results,
            "statistics": stats,
            "source": "PowerFlow (Athena)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "PowerFlow (Athena)"}


@register_factory("powerflow_connector")
@apex_action(
    name="get_contract_line_items",
    description="Get line items for a specific contract",
    industry="aerospace_defense"
)
def get_contract_line_items(contract_number: str) -> Dict[str, Any]:
    """
    Get all line items (CLINs) for a specific contract.

    Args:
        contract_number: Contract number to query

    Returns:
        Contract details with line items
    """
    connector = AthenaConnector()

    # Get contract header
    contract_query = f"""
    SELECT * FROM contracts
    WHERE contract_number = '{contract_number}'
    ORDER BY modification DESC
    LIMIT 1
    """

    # Get line items
    items_query = f"""
    SELECT * FROM contract_line_items
    WHERE contract_number = '{contract_number}'
    ORDER BY clin
    """

    try:
        contract = connector.execute_query(contract_query)
        items = connector.execute_query(items_query)

        if not contract:
            return {"error": f"Contract {contract_number} not found"}

        return {
            "contract": contract[0],
            "line_items": items,
            "total_clins": len(items),
            "source": "PowerFlow (Athena)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "PowerFlow (Athena)"}
