#!/usr/bin/env python3
"""
Add Action Groups to APEX Aerospace Bedrock Agents
Creates Lambda functions that the Bedrock Agents can call as tools
"""
import boto3
import json
import zipfile
import io
import time

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# Existing Bedrock Agent IDs
AGENT_IDS = {
    "apex-contract-bot": "SQKAE9HBA6",
    "apex-cnc-bot": "ELJXYFD4EI",
    "apex-workorder-bot": "HDDMKPONTA"
}

# IAM Role for action group Lambda functions
LAMBDA_ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/apex-ai-platform-lambda-role"


# =====================================================================
# ACTION GROUP LAMBDA HANDLERS
# These follow Bedrock Agent action group response format
# =====================================================================

CONTRACT_BOT_ACTION_HANDLER = '''
import json
import boto3
import time
from decimal import Decimal

athena = boto3.client('athena', region_name='us-east-1')

ATHENA_DATABASE = "powerflow_demo"
S3_OUTPUT = "s3://apex-demo-athena-results/"


def execute_athena_query(query, timeout=30):
    """Execute Athena query and return results."""
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': ATHENA_DATABASE},
            ResultConfiguration={'OutputLocation': S3_OUTPUT}
        )
        query_id = response['QueryExecutionId']

        for _ in range(timeout):
            status = athena.get_query_execution(QueryExecutionId=query_id)
            state = status['QueryExecution']['Status']['State']
            if state == 'SUCCEEDED':
                break
            elif state in ['FAILED', 'CANCELLED']:
                return {"error": status['QueryExecution']['Status'].get('StateChangeReason', 'Query failed')}
            time.sleep(1)

        results = athena.get_query_results(QueryExecutionId=query_id)
        columns = [col['Name'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        for row in results['ResultSet']['Rows'][1:]:
            values = [field.get('VarCharValue', '') for field in row['Data']]
            rows.append(dict(zip(columns, values)))
        return rows
    except Exception as e:
        return {"error": str(e)}


def query_contracts(program=None, prime_contractor=None, limit=10):
    """Query contracts from Athena."""
    query = "SELECT contract_number, program, prime_contractor, award_date, total_value, security_classification FROM contracts WHERE 1=1"
    if program:
        query += f" AND UPPER(program) = UPPER('{program}')"
    if prime_contractor:
        query += f" AND LOWER(prime_contractor) LIKE LOWER('%{prime_contractor}%')"
    query += f" ORDER BY award_date DESC LIMIT {limit}"
    results = execute_athena_query(query)
    return {"contracts": results, "total": len(results) if isinstance(results, list) else 0, "source": "PowerFlow (Athena)"}


def get_pricing_history(part_number):
    """Get pricing history for a part number."""
    query = f"""
    SELECT part_number, contract_number, award_date, quantity, unit_price, material, program
    FROM pricing_history WHERE part_number = '{part_number}' ORDER BY award_date DESC
    """
    results = execute_athena_query(query)
    if isinstance(results, list) and results:
        prices = [float(r['unit_price']) for r in results if r.get('unit_price')]
        return {
            "part_number": part_number,
            "records": results,
            "statistics": {
                "avg_price": round(sum(prices)/len(prices), 2) if prices else 0,
                "min_price": min(prices) if prices else 0,
                "max_price": max(prices) if prices else 0
            },
            "source": "PowerFlow (Athena)"
        }
    return {"error": f"No pricing history for {part_number}"}


def handler(event, context):
    """Bedrock Agent Action Group handler."""
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    result = {}

    if api_path == '/query_contracts':
        result = query_contracts(
            program=parameters.get('program'),
            prime_contractor=parameters.get('prime_contractor'),
            limit=int(parameters.get('limit', 10))
        )
    elif api_path == '/get_pricing_history':
        result = get_pricing_history(parameters.get('part_number', ''))
    else:
        result = {"error": f"Unknown API path: {api_path}"}

    # Bedrock Agent response format
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': 'GET',
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result)
                }
            }
        }
    }
'''

CNC_BOT_ACTION_HANDLER = '''
import json
import boto3

s3 = boto3.client('s3', region_name='us-east-1')
BUCKET = "apex-demo-cad-vault"


def get_gcode_program(program_name):
    """Get G-code from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET, Key=f"programs/{program_name}")
        content = response['Body'].read().decode('utf-8')
        return {"program_name": program_name, "content": content, "source": "CNC Repository (S3)"}
    except Exception as e:
        return {"error": f"Program {program_name} not found: {str(e)}"}


def list_gcode_programs(part_number=None):
    """List available G-code programs."""
    try:
        response = s3.list_objects_v2(Bucket=BUCKET, Prefix="programs/")
        programs = [obj['Key'].split('/')[-1] for obj in response.get('Contents', []) if obj['Key'].endswith('.nc')]
        if part_number:
            programs = [p for p in programs if part_number.lower() in p.lower()]
        return {"programs": programs, "total": len(programs), "source": "CNC Repository (S3)"}
    except Exception as e:
        return {"error": str(e)}


def handler(event, context):
    """Bedrock Agent Action Group handler."""
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    result = {}

    if api_path == '/get_gcode_program':
        result = get_gcode_program(parameters.get('program_name', ''))
    elif api_path == '/list_gcode_programs':
        result = list_gcode_programs(parameters.get('part_number'))
    else:
        result = {"error": f"Unknown API path: {api_path}"}

    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': 'GET',
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result)
                }
            }
        }
    }
'''

WORKORDER_BOT_ACTION_HANDLER = '''
import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
WO_TABLE = dynamodb.Table('apex-demo-work-orders')
NCR_TABLE = dynamodb.Table('apex-demo-ncr')
AUDIT_TABLE = dynamodb.Table('apex-demo-audit-log')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def query_work_order(work_order_id):
    """Query work order from DynamoDB."""
    try:
        response = WO_TABLE.get_item(Key={'work_order_id': work_order_id})
        if 'Item' in response:
            return {"work_order": response['Item'], "source": "GovCloud ERP (DynamoDB)"}
        return {"error": f"Work order {work_order_id} not found"}
    except Exception as e:
        return {"error": str(e)}


def list_work_orders(status=None, program=None, priority=None):
    """List work orders with optional filters."""
    try:
        response = WO_TABLE.scan()
        items = response.get('Items', [])
        if status:
            items = [i for i in items if i.get('status', '').upper() == status.upper()]
        if program:
            items = [i for i in items if i.get('program', '').upper() == program.upper()]
        if priority:
            items = [i for i in items if i.get('priority', '').upper() == priority.upper()]
        return {"work_orders": items, "total": len(items), "source": "GovCloud ERP (DynamoDB)"}
    except Exception as e:
        return {"error": str(e)}


def update_work_order_status(work_order_id, new_status, notes=None):
    """Update work order status (WRITE operation)."""
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"

        update_expr = "SET #status = :status, updated_at = :ts"
        expr_values = {":status": new_status.upper(), ":ts": timestamp}
        expr_names = {"#status": "status"}

        if notes:
            update_expr += ", notes = :notes"
            expr_values[":notes"] = notes

        WO_TABLE.update_item(
            Key={'work_order_id': work_order_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )

        # Audit log for NIST 800-171 compliance
        AUDIT_TABLE.put_item(Item={
            'audit_id': f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'timestamp': timestamp,
            'operation': 'update_work_order',
            'record_id': work_order_id,
            'changes': json.dumps({'status': new_status, 'notes': notes}),
            'user_id': 'APEX_WORKORDER_BOT'
        })

        return {"success": True, "work_order_id": work_order_id, "new_status": new_status, "mode": "WRITE", "audit_logged": True}
    except Exception as e:
        return {"error": str(e)}


def create_ncr(work_order_id, defect_type, defect_description, quantity_affected):
    """Create Non-Conformance Report (WRITE operation)."""
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        ncr_id = f"NCR-{datetime.utcnow().strftime('%Y-%m%d%H%M%S')}"

        NCR_TABLE.put_item(Item={
            'ncr_id': ncr_id,
            'work_order_id': work_order_id,
            'defect_type': defect_type,
            'defect_description': defect_description,
            'quantity_affected': int(quantity_affected),
            'status': 'OPEN',
            'created_at': timestamp,
            'created_by': 'APEX_WORKORDER_BOT'
        })

        # Audit log
        AUDIT_TABLE.put_item(Item={
            'audit_id': f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-NCR",
            'timestamp': timestamp,
            'operation': 'create_ncr',
            'record_id': ncr_id,
            'changes': json.dumps({'work_order_id': work_order_id, 'defect_type': defect_type}),
            'user_id': 'APEX_WORKORDER_BOT'
        })

        return {"success": True, "ncr_id": ncr_id, "work_order_id": work_order_id, "mode": "WRITE", "audit_logged": True}
    except Exception as e:
        return {"error": str(e)}


def handler(event, context):
    """Bedrock Agent Action Group handler."""
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    result = {}

    if api_path == '/query_work_order':
        result = query_work_order(parameters.get('work_order_id', ''))
    elif api_path == '/list_work_orders':
        result = list_work_orders(
            status=parameters.get('status'),
            program=parameters.get('program'),
            priority=parameters.get('priority')
        )
    elif api_path == '/update_work_order_status':
        result = update_work_order_status(
            parameters.get('work_order_id', ''),
            parameters.get('new_status', ''),
            parameters.get('notes')
        )
    elif api_path == '/create_ncr':
        result = create_ncr(
            parameters.get('work_order_id', ''),
            parameters.get('defect_type', ''),
            parameters.get('defect_description', ''),
            parameters.get('quantity_affected', 1)
        )
    else:
        result = {"error": f"Unknown API path: {api_path}"}

    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': 'POST' if 'update' in api_path or 'create' in api_path else 'GET',
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result, cls=DecimalEncoder)
                }
            }
        }
    }
'''


# =====================================================================
# OPENAPI SCHEMAS FOR ACTION GROUPS
# =====================================================================

CONTRACT_BOT_SCHEMA = {
    "openapi": "3.0.0",
    "info": {"title": "ContractBot Actions", "version": "1.0.0"},
    "paths": {
        "/query_contracts": {
            "get": {
                "summary": "Query defense contracts from PowerFlow database",
                "description": "Search contracts by program (F-35, F-22, UH-60, C-17), prime contractor, or retrieve all contracts",
                "operationId": "queryContracts",
                "parameters": [
                    {"name": "program", "in": "query", "description": "Program name (F-35, F-22, UH-60, C-17)", "schema": {"type": "string"}},
                    {"name": "prime_contractor", "in": "query", "description": "Prime contractor name", "schema": {"type": "string"}},
                    {"name": "limit", "in": "query", "description": "Maximum results", "schema": {"type": "integer", "default": 10}}
                ],
                "responses": {"200": {"description": "Contract data from PowerFlow"}}
            }
        },
        "/get_pricing_history": {
            "get": {
                "summary": "Get historical pricing for a part number",
                "description": "Retrieve pricing history across contracts for a specific part number. Use for price analysis and RFP pricing.",
                "operationId": "getPricingHistory",
                "parameters": [
                    {"name": "part_number", "in": "query", "required": True, "description": "Part number (e.g., TG-5842-001)", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Pricing history with statistics"}}
            }
        }
    }
}

CNC_BOT_SCHEMA = {
    "openapi": "3.0.0",
    "info": {"title": "CNCBot Actions", "version": "1.0.0"},
    "paths": {
        "/get_gcode_program": {
            "get": {
                "summary": "Retrieve a G-code program from the CNC repository",
                "description": "Get the full G-code content for analysis and review",
                "operationId": "getGcodeProgram",
                "parameters": [
                    {"name": "program_name", "in": "query", "required": True, "description": "Program filename (e.g., TG-5842-001-REV-D.nc)", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "G-code program content"}}
            }
        },
        "/list_gcode_programs": {
            "get": {
                "summary": "List available G-code programs",
                "description": "List all G-code programs, optionally filtered by part number",
                "operationId": "listGcodePrograms",
                "parameters": [
                    {"name": "part_number", "in": "query", "description": "Filter by part number", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "List of available programs"}}
            }
        }
    }
}

WORKORDER_BOT_SCHEMA = {
    "openapi": "3.0.0",
    "info": {"title": "WorkOrderBot Actions", "version": "1.0.0"},
    "paths": {
        "/query_work_order": {
            "get": {
                "summary": "Query a specific work order by ID",
                "description": "Get full details of a work order including status, operations, and quality holds",
                "operationId": "queryWorkOrder",
                "parameters": [
                    {"name": "work_order_id", "in": "query", "required": True, "description": "Work order ID (e.g., WO-2026-001187)", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Work order details"}}
            }
        },
        "/list_work_orders": {
            "get": {
                "summary": "List work orders with optional filters",
                "description": "List work orders filtered by status, program, or priority",
                "operationId": "listWorkOrders",
                "parameters": [
                    {"name": "status", "in": "query", "description": "Filter by status (OPEN, IN_PROGRESS, ON_HOLD, COMPLETE)", "schema": {"type": "string"}},
                    {"name": "program", "in": "query", "description": "Filter by program (F-35, F-22, etc.)", "schema": {"type": "string"}},
                    {"name": "priority", "in": "query", "description": "Filter by priority (AOG, CRITICAL, HIGH, NORMAL)", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "List of work orders"}}
            }
        },
        "/update_work_order_status": {
            "post": {
                "summary": "Update work order status (WRITE operation)",
                "description": "Update the status of a work order. All changes are logged for NIST 800-171 compliance.",
                "operationId": "updateWorkOrderStatus",
                "parameters": [
                    {"name": "work_order_id", "in": "query", "required": True, "description": "Work order ID", "schema": {"type": "string"}},
                    {"name": "new_status", "in": "query", "required": True, "description": "New status (IN_PROGRESS, COMPLETE, ON_HOLD, CLOSED)", "schema": {"type": "string"}},
                    {"name": "notes", "in": "query", "description": "Optional notes", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Update confirmation"}}
            }
        },
        "/create_ncr": {
            "post": {
                "summary": "Create a Non-Conformance Report (WRITE operation)",
                "description": "Create an NCR for quality issues. Logged for AS9100D compliance.",
                "operationId": "createNcr",
                "parameters": [
                    {"name": "work_order_id", "in": "query", "required": True, "description": "Work order ID", "schema": {"type": "string"}},
                    {"name": "defect_type", "in": "query", "required": True, "description": "Type of defect", "schema": {"type": "string"}},
                    {"name": "defect_description", "in": "query", "required": True, "description": "Description of the defect", "schema": {"type": "string"}},
                    {"name": "quantity_affected", "in": "query", "required": True, "description": "Number of units affected", "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "NCR creation confirmation"}}
            }
        }
    }
}


def create_lambda_package(handler_code: str) -> bytes:
    """Create deployment package for Lambda."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('lambda_function.py', handler_code)
    buffer.seek(0)
    return buffer.read()


def create_or_update_lambda(lambda_client, function_name: str, handler_code: str, description: str):
    """Create or update Lambda function."""
    package = create_lambda_package(handler_code)

    try:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=package
        )
        print(f"  Updated Lambda: {function_name}")

        # Wait for update to complete
        time.sleep(3)
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Description=description,
            Timeout=120,
            MemorySize=512
        )
    except lambda_client.exceptions.ResourceNotFoundException:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=LAMBDA_ROLE_ARN,
            Handler='lambda_function.handler',
            Code={'ZipFile': package},
            Description=description,
            Timeout=120,
            MemorySize=512,
            Tags={'Project': 'APEX', 'Industry': 'aerospace_defense'}
        )
        print(f"  Created Lambda: {function_name}")

    return f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{function_name}"


def add_lambda_permission(lambda_client, function_name: str, agent_id: str):
    """Add permission for Bedrock Agent to invoke Lambda."""
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'BedrockAgent-{agent_id}',
            Action='lambda:InvokeFunction',
            Principal='bedrock.amazonaws.com',
            SourceArn=f'arn:aws:bedrock:{REGION}:{ACCOUNT_ID}:agent/{agent_id}'
        )
        print(f"  Added Bedrock Agent permission to {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"  Permission already exists for {function_name}")


def create_action_group(bedrock_agent, agent_id: str, action_group_name: str,
                        description: str, lambda_arn: str, api_schema: dict):
    """Create or update action group on Bedrock Agent."""
    try:
        # Check if action group exists
        existing = bedrock_agent.list_agent_action_groups(agentId=agent_id, agentVersion='DRAFT')
        for ag in existing.get('actionGroupSummaries', []):
            if ag['actionGroupName'] == action_group_name:
                # Update existing
                bedrock_agent.update_agent_action_group(
                    agentId=agent_id,
                    agentVersion='DRAFT',
                    actionGroupId=ag['actionGroupId'],
                    actionGroupName=action_group_name,
                    description=description,
                    actionGroupExecutor={'lambda': lambda_arn},
                    apiSchema={'payload': json.dumps(api_schema)}
                )
                print(f"  Updated action group: {action_group_name}")
                return ag['actionGroupId']

        # Create new
        response = bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName=action_group_name,
            description=description,
            actionGroupExecutor={'lambda': lambda_arn},
            apiSchema={'payload': json.dumps(api_schema)}
        )
        print(f"  Created action group: {action_group_name}")
        return response['agentActionGroup']['actionGroupId']

    except Exception as e:
        print(f"  Error creating action group: {e}")
        raise


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - ACTION GROUPS SETUP")
    print("=" * 60)

    lambda_client = boto3.client('lambda', region_name=REGION)
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)

    # Configuration for each agent
    agents_config = [
        {
            "agent_name": "apex-contract-bot",
            "agent_id": AGENT_IDS["apex-contract-bot"],
            "lambda_name": "apex-contract-bot-actions",
            "handler_code": CONTRACT_BOT_ACTION_HANDLER,
            "action_group_name": "ContractActions",
            "description": "Query contracts and pricing from PowerFlow database (Athena)",
            "schema": CONTRACT_BOT_SCHEMA
        },
        {
            "agent_name": "apex-cnc-bot",
            "agent_id": AGENT_IDS["apex-cnc-bot"],
            "lambda_name": "apex-cnc-bot-actions",
            "handler_code": CNC_BOT_ACTION_HANDLER,
            "action_group_name": "CNCActions",
            "description": "Retrieve and list G-code programs from CNC repository (S3)",
            "schema": CNC_BOT_SCHEMA
        },
        {
            "agent_name": "apex-workorder-bot",
            "agent_id": AGENT_IDS["apex-workorder-bot"],
            "lambda_name": "apex-workorder-bot-actions",
            "handler_code": WORKORDER_BOT_ACTION_HANDLER,
            "action_group_name": "WorkOrderActions",
            "description": "Query and manage work orders in GovCloud ERP (DynamoDB)",
            "schema": WORKORDER_BOT_SCHEMA
        }
    ]

    for config in agents_config:
        print(f"\n=== Setting up {config['agent_name']} ===")

        # 1. Create/Update Lambda function
        lambda_arn = create_or_update_lambda(
            lambda_client,
            config['lambda_name'],
            config['handler_code'],
            config['description']
        )

        # 2. Add permission for Bedrock Agent to invoke Lambda
        add_lambda_permission(lambda_client, config['lambda_name'], config['agent_id'])

        # 3. Create/Update Action Group
        create_action_group(
            bedrock_agent,
            config['agent_id'],
            config['action_group_name'],
            config['description'],
            lambda_arn,
            config['schema']
        )

    # 4. Re-prepare all agents
    print("\n=== Preparing Agents ===")
    for agent_name, agent_id in AGENT_IDS.items():
        try:
            bedrock_agent.prepare_agent(agentId=agent_id)
            print(f"  Preparing {agent_name}...")
        except Exception as e:
            print(f"  Error preparing {agent_name}: {e}")

    # Wait for preparation
    print("\n  Waiting for agents to be ready...")
    time.sleep(10)

    # Verify status
    print("\n=== Deployment Summary ===")
    for agent_name, agent_id in AGENT_IDS.items():
        status = bedrock_agent.get_agent(agentId=agent_id)
        agent_status = status['agent']['agentStatus']
        print(f"\n{agent_name}:")
        print(f"  Agent ID: {agent_id}")
        print(f"  Status: {agent_status}")

        # List action groups
        action_groups = bedrock_agent.list_agent_action_groups(agentId=agent_id, agentVersion='DRAFT')
        for ag in action_groups.get('actionGroupSummaries', []):
            print(f"  Action Group: {ag['actionGroupName']} ({ag['actionGroupState']})")

    print("\n" + "=" * 60)
    print("To test an agent:")
    print('  aws bedrock-agent-runtime invoke-agent \\')
    print('    --agent-id SQKAE9HBA6 \\')
    print('    --agent-alias-id TSTALIASID \\')
    print('    --session-id test-session \\')
    print('    --input-text "Show F-35 contracts"')
    print("=" * 60)


if __name__ == "__main__":
    main()
