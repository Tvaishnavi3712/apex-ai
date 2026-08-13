#!/usr/bin/env python3
"""
Deploy APEX Aerospace Agents as Lambda Functions v2
- Uses Claude Opus 4.6 model
- Integrates with Athena, DynamoDB, S3 connectors
"""
import boto3
import json
import zipfile
import os
import io
from pathlib import Path

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# Claude Opus 4.6 Model ID
CLAUDE_OPUS_MODEL = "us.anthropic.claude-opus-4-6-v1"

# Agent configurations
AGENTS = {
    "apex-contract-bot": {
        "description": "Contract analysis and pricing for defense programs",
        "memory": 1024,
        "timeout": 300,
        "system_prompt": """You are ContractBot, an AI assistant for Essex Industries aerospace & defense.

Your capabilities:
1. Query defense contracts from PowerFlow database (Athena)
2. Analyze historical pricing across programs (F-35, F-22, UH-60, C-17)
3. Predict pricing for new RFPs
4. Generate price justification narratives

Available tools:
- query_contracts(program, part_number, prime_contractor, limit)
- get_pricing_history(part_number)
- get_contract_line_items(contract_number)

All data is ITAR controlled. Comply with NIST 800-171."""
    },
    "apex-cnc-bot": {
        "description": "CNC G-code analysis and optimization",
        "memory": 512,
        "timeout": 120,
        "system_prompt": """You are CNCBot, an AI assistant for CNC programming at Essex Industries.

Your capabilities:
1. Review G-code for syntax and safety issues
2. Validate feeds/speeds for materials (Ti-6Al-4V, 7075-T6, Inconel-718)
3. Suggest optimizations
4. Find similar historical programs

Available tools:
- get_gcode_program(program_name)
- list_gcode_programs(part_number)

Material specs:
- Ti-6Al-4V: SFM 100-150, high-pressure coolant required
- 7075-T6: SFM 800-1500, flood coolant
- Inconel-718: SFM 60-100, very difficult material

You ASSIST the machinist - all changes require human approval."""
    },
    "apex-workorder-bot": {
        "description": "Work order management with ERP read/write",
        "memory": 512,
        "timeout": 120,
        "system_prompt": """You are WorkOrderBot, an AI assistant for work order management at Essex Industries.

Your capabilities (READ):
- Query work order status
- List work orders by program, status, priority
- Get associated documents

Your capabilities (WRITE):
- Update work order status
- Create new work orders
- Create Non-Conformance Reports (NCRs)

Available tools:
- query_work_order(work_order_id)
- list_work_orders(status, program, priority)
- update_work_order_status(work_order_id, new_status, quantity_complete, notes)
- create_work_order(part_number, quantity, required_date, program, customer_po, priority)
- create_ncr(work_order_id, defect_type, defect_description, quantity_affected)

All WRITE operations are logged for NIST 800-171 compliance."""
    }
}


def create_contract_bot_handler() -> str:
    """Create Lambda handler for ContractBot with Athena integration."""
    return '''
import json
import boto3
import time
from typing import Optional, Dict, Any, List

# Clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
athena = boto3.client('athena', region_name='us-east-1')

ATHENA_DATABASE = "powerflow_demo"
S3_OUTPUT = "s3://apex-demo-athena-results/"
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"

SYSTEM_PROMPT = """You are ContractBot, an AI assistant for Essex Industries aerospace & defense.

You have access to the PowerFlow contract database via Athena. When users ask about contracts,
use the tool results provided to give accurate answers.

All data is ITAR controlled. Comply with NIST 800-171 and CMMC requirements.
Always cite contract numbers and specific data from the query results."""


def execute_athena_query(query: str, timeout: int = 30) -> List[Dict]:
    """Execute Athena query and return results."""
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
            return [{"error": status['QueryExecution']['Status'].get('StateChangeReason', 'Query failed')}]
        time.sleep(1)

    results = athena.get_query_results(QueryExecutionId=query_id)
    columns = [col['Name'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = []
    for row in results['ResultSet']['Rows'][1:]:
        values = [field.get('VarCharValue', '') for field in row['Data']]
        rows.append(dict(zip(columns, values)))
    return rows


def query_contracts(program: Optional[str] = None, part_number: Optional[str] = None,
                   prime_contractor: Optional[str] = None, limit: int = 10) -> Dict:
    """Query contracts from Athena."""
    query = "SELECT contract_number, program, prime_contractor, award_date, total_value, security_classification FROM contracts WHERE 1=1"
    if program:
        query += f" AND UPPER(program) = UPPER('{program}')"
    if prime_contractor:
        query += f" AND LOWER(prime_contractor) LIKE LOWER('%{prime_contractor}%')"
    query += f" ORDER BY award_date DESC LIMIT {limit}"

    results = execute_athena_query(query)
    return {"contracts": results, "total": len(results), "source": "PowerFlow (Athena)"}


def get_pricing_history(part_number: str) -> Dict:
    """Get pricing history for a part number."""
    query = f"""
    SELECT part_number, contract_number, award_date, quantity, unit_price, material, program
    FROM pricing_history WHERE part_number = '{part_number}' ORDER BY award_date DESC
    """
    results = execute_athena_query(query)
    if results:
        prices = [float(r['unit_price']) for r in results if r.get('unit_price')]
        return {
            "part_number": part_number,
            "records": results,
            "statistics": {
                "avg_price": sum(prices)/len(prices) if prices else 0,
                "min_price": min(prices) if prices else 0,
                "max_price": max(prices) if prices else 0
            },
            "source": "PowerFlow (Athena)"
        }
    return {"error": f"No pricing history for {part_number}"}


def handler(event, context):
    """Lambda handler for ContractBot."""
    try:
        prompt = event.get('prompt', event.get('body', ''))
        if isinstance(prompt, str) and prompt.startswith('{'):
            prompt = json.loads(prompt).get('prompt', prompt)

        # Detect intent and query data
        prompt_lower = prompt.lower()
        tool_results = []

        if any(word in prompt_lower for word in ['contract', 'f-35', 'f-22', 'uh-60', 'c-17', 'lockheed', 'sikorsky', 'boeing']):
            # Extract program if mentioned
            program = None
            for p in ['F-35', 'F-22', 'UH-60', 'C-17']:
                if p.lower() in prompt_lower:
                    program = p
                    break
            contracts = query_contracts(program=program, limit=10)
            tool_results.append(f"CONTRACT DATA:\\n{json.dumps(contracts, indent=2)}")

        if any(word in prompt_lower for word in ['pricing', 'price', 'history', 'tg-', 'ss-', 'cg-']):
            # Extract part number if mentioned
            import re
            pn_match = re.search(r'(TG|SS|CG)-\\d{4}-\\d{3}', prompt, re.IGNORECASE)
            if pn_match:
                history = get_pricing_history(pn_match.group().upper())
                tool_results.append(f"PRICING HISTORY:\\n{json.dumps(history, indent=2)}")

        # Build message with tool results
        user_content = prompt
        if tool_results:
            user_content = f"{prompt}\\n\\n--- DATA FROM POWERFLOW DATABASE ---\\n" + "\\n".join(tool_results)

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': user_content}],
                'system': SYSTEM_PROMPT
            })
        )

        result = json.loads(response['body'].read())
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result['content'][0]['text'],
                'agent': 'apex-contract-bot',
                'model': 'Claude Opus 4.6',
                'data_source': 'PowerFlow (Athena)'
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
'''


def create_cnc_bot_handler() -> str:
    """Create Lambda handler for CNCBot with S3 integration."""
    return '''
import json
import boto3
import re

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

BUCKET = "apex-demo-cad-vault"
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"

SYSTEM_PROMPT = """You are CNCBot, an AI assistant for CNC programming at Essex Industries.

When reviewing G-code:
1. Check spindle speeds against material recommendations
2. Verify coolant commands (M8/M08) before cutting
3. Check Z clearance on rapids (minimum 0.25")
4. Validate feed rates for the material

Material specs:
- Ti-6Al-4V: SFM 100-150, feed 0.002-0.006 IPT, HIGH PRESSURE COOLANT REQUIRED
- 7075-T6: SFM 800-1500, feed 0.004-0.012 IPT, flood coolant OK
- 15-5PH: SFM 150-250, feed 0.003-0.008 IPT
- Inconel-718: SFM 60-100, feed 0.002-0.005 IPT, VERY DIFFICULT

You ASSIST the machinist - all recommendations require human approval."""


def get_gcode_program(program_name: str) -> dict:
    """Get G-code from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET, Key=f"programs/{program_name}")
        return {"program_name": program_name, "content": response['Body'].read().decode('utf-8')}
    except:
        return {"error": f"Program {program_name} not found"}


def list_gcode_programs() -> dict:
    """List available G-code programs."""
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix="programs/")
    programs = [obj['Key'].split('/')[-1] for obj in response.get('Contents', []) if obj['Key'].endswith('.nc')]
    return {"programs": programs, "total": len(programs)}


def handler(event, context):
    try:
        prompt = event.get('prompt', event.get('body', ''))
        if isinstance(prompt, str) and prompt.startswith('{'):
            prompt = json.loads(prompt).get('prompt', prompt)

        tool_results = []
        prompt_lower = prompt.lower()

        # Check if user wants to list programs
        if 'list' in prompt_lower or 'available' in prompt_lower or 'programs' in prompt_lower:
            programs = list_gcode_programs()
            tool_results.append(f"AVAILABLE PROGRAMS:\\n{json.dumps(programs, indent=2)}")

        # Check for specific program or G-code in the prompt
        nc_match = re.search(r'[\\w-]+\\.nc', prompt, re.IGNORECASE)
        if nc_match:
            gcode = get_gcode_program(nc_match.group())
            if 'content' in gcode:
                tool_results.append(f"G-CODE PROGRAM ({nc_match.group()}):\\n{gcode['content']}")

        # Check if G-code is directly in the prompt
        if 'G90' in prompt or 'G0' in prompt or 'G1' in prompt or 'N10' in prompt:
            tool_results.append("G-CODE PROVIDED IN PROMPT - Analyzing...")

        user_content = prompt
        if tool_results:
            user_content = f"{prompt}\\n\\n--- DATA FROM CNC REPOSITORY ---\\n" + "\\n".join(tool_results)

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': user_content}],
                'system': SYSTEM_PROMPT
            })
        )

        result = json.loads(response['body'].read())
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result['content'][0]['text'],
                'agent': 'apex-cnc-bot',
                'model': 'Claude Opus 4.6',
                'data_source': 'CNC Repository (S3)'
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
'''


def create_workorder_bot_handler() -> str:
    """Create Lambda handler for WorkOrderBot with DynamoDB integration."""
    return '''
import json
import boto3
from datetime import datetime
from decimal import Decimal

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

WO_TABLE = dynamodb.Table('apex-demo-work-orders')
OPS_TABLE = dynamodb.Table('apex-demo-wo-operations')
NCR_TABLE = dynamodb.Table('apex-demo-ncr')
AUDIT_TABLE = dynamodb.Table('apex-demo-audit-log')

MODEL_ID = "us.anthropic.claude-opus-4-6-v1"

SYSTEM_PROMPT = """You are WorkOrderBot, an AI assistant for work order management at Essex Industries.

You have READ and WRITE access to the GovCloud ERP (DynamoDB).

READ operations:
- Query work order status and details
- List work orders by filters

WRITE operations (require confirmation):
- Update work order status
- Create new work orders
- Create NCRs (Non-Conformance Reports)

All WRITE operations are logged for NIST 800-171 compliance.
When updating status, valid values are: OPEN, IN_PROGRESS, ON_HOLD, COMPLETE, CLOSED"""


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def query_work_order(work_order_id: str) -> dict:
    """Query work order from DynamoDB."""
    response = WO_TABLE.get_item(Key={'work_order_id': work_order_id})
    if 'Item' in response:
        return {"work_order": response['Item'], "source": "GovCloud ERP (DynamoDB)"}
    return {"error": f"Work order {work_order_id} not found"}


def list_work_orders(status: str = None, program: str = None) -> dict:
    """List work orders with optional filters."""
    response = WO_TABLE.scan()
    items = response.get('Items', [])
    if status:
        items = [i for i in items if i.get('status', '').upper() == status.upper()]
    if program:
        items = [i for i in items if i.get('program', '').upper() == program.upper()]
    return {"work_orders": items, "total": len(items), "source": "GovCloud ERP (DynamoDB)"}


def update_work_order_status(work_order_id: str, new_status: str, notes: str = None) -> dict:
    """Update work order status (WRITE)."""
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

    # Audit log
    AUDIT_TABLE.put_item(Item={
        'audit_id': f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        'timestamp': timestamp,
        'operation': 'update_work_order',
        'record_id': work_order_id,
        'changes': json.dumps({'status': new_status, 'notes': notes}),
        'user_id': 'APEX_SYSTEM'
    })

    return {"success": True, "work_order_id": work_order_id, "new_status": new_status, "mode": "WRITE"}


def handler(event, context):
    try:
        prompt = event.get('prompt', event.get('body', ''))
        if isinstance(prompt, str) and prompt.startswith('{'):
            prompt = json.loads(prompt).get('prompt', prompt)

        tool_results = []
        prompt_lower = prompt.lower()

        # Detect work order ID
        import re
        wo_match = re.search(r'WO-\\d{4}-\\d{6}', prompt, re.IGNORECASE)

        if wo_match:
            wo = query_work_order(wo_match.group().upper())
            tool_results.append(f"WORK ORDER DATA:\\n{json.dumps(wo, indent=2, cls=DecimalEncoder)}")

        if 'list' in prompt_lower or 'show all' in prompt_lower or 'work orders' in prompt_lower:
            status = None
            program = None
            for s in ['open', 'in_progress', 'on_hold', 'complete']:
                if s in prompt_lower:
                    status = s.upper()
            for p in ['f-35', 'f-22', 'uh-60', 'c-17']:
                if p in prompt_lower:
                    program = p.upper()
            wos = list_work_orders(status=status, program=program)
            tool_results.append(f"WORK ORDER LIST:\\n{json.dumps(wos, indent=2, cls=DecimalEncoder)}")

        # Handle WRITE operations
        if 'update' in prompt_lower and wo_match:
            for status in ['complete', 'in_progress', 'on_hold', 'closed']:
                if status in prompt_lower:
                    result = update_work_order_status(wo_match.group().upper(), status.upper())
                    tool_results.append(f"UPDATE RESULT:\\n{json.dumps(result, indent=2)}")
                    break

        user_content = prompt
        if tool_results:
            user_content = f"{prompt}\\n\\n--- DATA FROM GOVCLOUD ERP ---\\n" + "\\n".join(tool_results)

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': user_content}],
                'system': SYSTEM_PROMPT
            })
        )

        result = json.loads(response['body'].read())
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result['content'][0]['text'],
                'agent': 'apex-workorder-bot',
                'model': 'Claude Opus 4.6',
                'data_source': 'GovCloud ERP (DynamoDB)'
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
'''


def create_lambda_package(agent_name: str) -> bytes:
    """Create deployment package for Lambda."""
    buffer = io.BytesIO()

    handlers = {
        "apex-contract-bot": create_contract_bot_handler,
        "apex-cnc-bot": create_cnc_bot_handler,
        "apex-workorder-bot": create_workorder_bot_handler
    }

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        handler_code = handlers[agent_name]()
        zf.writestr('lambda_handler.py', handler_code)

    buffer.seek(0)
    return buffer.read()


def deploy_agent(agent_name: str, config: dict):
    """Deploy a single agent as Lambda function."""
    lambda_client = boto3.client('lambda', region_name=REGION)

    function_name = agent_name.replace('-', '_')
    role_arn = f'arn:aws:iam::{ACCOUNT_ID}:role/{agent_name}-role'

    print(f"\n=== Deploying {agent_name} (Claude Opus 4.6) ===")

    package = create_lambda_package(agent_name)
    print(f"  📦 Created deployment package ({len(package)} bytes)")

    try:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=package
        )
        print(f"  🔄 Updated Lambda: {function_name}")

        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Description=f"{config['description']} - Claude Opus 4.6",
            Timeout=config['timeout'],
            MemorySize=config['memory']
        )

    except lambda_client.exceptions.ResourceNotFoundException:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler='lambda_handler.handler',
            Code={'ZipFile': package},
            Description=f"{config['description']} - Claude Opus 4.6",
            Timeout=config['timeout'],
            MemorySize=config['memory'],
            Environment={'Variables': {'AGENT_NAME': agent_name}}
        )
        print(f"  ✅ Created Lambda: {function_name}")

    # Get function URL
    try:
        url_response = lambda_client.get_function_url_config(FunctionName=function_name)
        print(f"  🔗 Function URL: {url_response['FunctionUrl']}")
    except:
        pass

    return function_name


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - LAMBDA DEPLOYMENT v2")
    print("Model: Claude Opus 4.6 (us.anthropic.claude-opus-4-6-v1)")
    print("=" * 60)

    deployed = []
    for agent_name, config in AGENTS.items():
        try:
            function_name = deploy_agent(agent_name, config)
            deployed.append((agent_name, function_name))
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    print("\\nData Connectors Integrated:")
    print("  - ContractBot → Athena (powerflow_demo)")
    print("  - CNCBot → S3 (apex-demo-cad-vault)")
    print("  - WorkOrderBot → DynamoDB (apex-demo-work-orders)")


if __name__ == "__main__":
    main()
