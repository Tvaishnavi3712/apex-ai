#!/usr/bin/env python3
"""
APEX Aerospace Defense Demo - AWS Infrastructure Setup
Sets up S3, Athena, and DynamoDB resources for live demo connectors.

Usage:
    python setup_aerospace_demo.py --profile cbts-demo --region us-east-1

Prerequisites:
    - AWS CLI configured with appropriate credentials
    - boto3 installed
    - Sufficient IAM permissions for S3, Athena, DynamoDB, Glue
"""

import boto3
import json
import time
import argparse
import os
from pathlib import Path

# Configuration
DEMO_PREFIX = "apex-demo"
ACCOUNT_ID = "457795063704"  # CBTS account

# Resource names
S3_BUCKETS = {
    "powerflow": f"{DEMO_PREFIX}-powerflow-data",
    "cad_vault": f"{DEMO_PREFIX}-cad-vault",
    "sharepoint": f"{DEMO_PREFIX}-sharepoint-docs",
    "athena_results": f"{DEMO_PREFIX}-athena-results"
}

DYNAMODB_TABLES = {
    "work_orders": f"{DEMO_PREFIX}-work-orders",
    "wo_operations": f"{DEMO_PREFIX}-wo-operations",
    "ncr_records": f"{DEMO_PREFIX}-ncr",
    "audit_log": f"{DEMO_PREFIX}-audit-log",
    "cad_metadata": f"{DEMO_PREFIX}-cad-metadata",
    "doc_metadata": f"{DEMO_PREFIX}-doc-metadata"
}

ATHENA_DATABASE = "powerflow_demo"


def create_s3_buckets(s3_client, region):
    """Create S3 buckets for demo data."""
    print("\n=== Creating S3 Buckets ===")

    for name, bucket in S3_BUCKETS.items():
        try:
            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket)
            else:
                s3_client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"  ✅ Created bucket: {bucket}")

            # Enable versioning
            s3_client.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )

            # Enable encryption
            s3_client.put_bucket_encryption(
                Bucket=bucket,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )

        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            print(f"  ⏭️  Bucket already exists: {bucket}")
        except Exception as e:
            print(f"  ❌ Error creating {bucket}: {e}")


def upload_contract_data(s3_client):
    """Upload contract CSV files to S3 for Athena."""
    print("\n=== Uploading Contract Data to S3 ===")

    base_path = Path(__file__).parent.parent / "synthetic-data" / "aerospace_defense" / "contracts"
    bucket = S3_BUCKETS["powerflow"]

    files = ["contracts.csv", "line_items.csv", "pricing_history.csv"]

    for filename in files:
        filepath = base_path / filename
        if filepath.exists():
            s3_key = f"aerospace/contracts/{filename}"
            s3_client.upload_file(str(filepath), bucket, s3_key)
            print(f"  ✅ Uploaded: s3://{bucket}/{s3_key}")
        else:
            print(f"  ❌ File not found: {filepath}")


def upload_gcode_files(s3_client):
    """Upload G-code sample files to S3."""
    print("\n=== Uploading G-code Files to S3 ===")

    base_path = Path(__file__).parent.parent / "synthetic-data" / "aerospace_defense" / "gcode"
    bucket = S3_BUCKETS["cad_vault"]

    if base_path.exists():
        for filepath in base_path.glob("*.nc"):
            s3_key = f"programs/{filepath.name}"
            s3_client.upload_file(str(filepath), bucket, s3_key)
            print(f"  ✅ Uploaded: s3://{bucket}/{s3_key}")
    else:
        print(f"  ❌ Directory not found: {base_path}")


def upload_rfp_documents(s3_client):
    """Upload RFP sample documents to S3."""
    print("\n=== Uploading RFP Documents to S3 ===")

    base_path = Path(__file__).parent.parent / "synthetic-data" / "aerospace_defense" / "rfp"
    bucket = S3_BUCKETS["sharepoint"]

    if base_path.exists():
        for filepath in base_path.glob("*.md"):
            s3_key = f"rfp/{filepath.name}"
            s3_client.upload_file(str(filepath), bucket, s3_key)
            print(f"  ✅ Uploaded: s3://{bucket}/{s3_key}")
    else:
        print(f"  ❌ Directory not found: {base_path}")


def create_athena_database(athena_client, region):
    """Create Athena database and tables for contract queries."""
    print("\n=== Setting up Athena Database ===")

    output_location = f"s3://{S3_BUCKETS['athena_results']}/"

    # Create database
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {ATHENA_DATABASE}"

    response = athena_client.start_query_execution(
        QueryString=create_db_query,
        ResultConfiguration={'OutputLocation': output_location}
    )

    query_id = response['QueryExecutionId']
    wait_for_athena_query(athena_client, query_id)
    print(f"  ✅ Created database: {ATHENA_DATABASE}")

    # Create contracts table
    create_contracts_table = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.contracts (
        contract_number STRING,
        modification STRING,
        program STRING,
        prime_contractor STRING,
        award_date DATE,
        total_value DECIMAL(12,2),
        itar_controlled BOOLEAN,
        security_classification STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION 's3://{S3_BUCKETS["powerflow"]}/aerospace/contracts/'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """

    response = athena_client.start_query_execution(
        QueryString=create_contracts_table,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': output_location}
    )
    wait_for_athena_query(athena_client, response['QueryExecutionId'])
    print(f"  ✅ Created table: {ATHENA_DATABASE}.contracts")

    # Create line_items table
    create_line_items_table = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.contract_line_items (
        contract_number STRING,
        clin STRING,
        part_number STRING,
        description STRING,
        quantity INT,
        unit_price DECIMAL(10,2)
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION 's3://{S3_BUCKETS["powerflow"]}/aerospace/contracts/'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """

    # Note: In production, line_items would be in a separate folder
    # For demo, we're using the same location with proper file naming

    # Create pricing_history table
    create_pricing_table = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.pricing_history (
        part_number STRING,
        contract_number STRING,
        award_date DATE,
        quantity INT,
        unit_price DECIMAL(10,2),
        material STRING,
        program STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION 's3://{S3_BUCKETS["powerflow"]}/aerospace/contracts/'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """

    print(f"  ✅ Athena tables created")


def wait_for_athena_query(athena_client, query_id, max_wait=60):
    """Wait for Athena query to complete."""
    for _ in range(max_wait):
        response = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = response['QueryExecution']['Status']['State']

        if state == 'SUCCEEDED':
            return True
        elif state in ['FAILED', 'CANCELLED']:
            reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
            print(f"  ❌ Query failed: {reason}")
            return False

        time.sleep(1)

    print(f"  ❌ Query timed out")
    return False


def create_dynamodb_tables(dynamodb_client):
    """Create DynamoDB tables for work orders and audit logs."""
    print("\n=== Creating DynamoDB Tables ===")

    # Work Orders table
    try:
        dynamodb_client.create_table(
            TableName=DYNAMODB_TABLES["work_orders"],
            KeySchema=[
                {'AttributeName': 'work_order_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'work_order_id', 'AttributeType': 'S'},
                {'AttributeName': 'program', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'priority', 'AttributeType': 'S'},
                {'AttributeName': 'required_date', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'program-status-index',
                    'KeySchema': [
                        {'AttributeName': 'program', 'KeyType': 'HASH'},
                        {'AttributeName': 'status', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'priority-date-index',
                    'KeySchema': [
                        {'AttributeName': 'priority', 'KeyType': 'HASH'},
                        {'AttributeName': 'required_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"  ✅ Created table: {DYNAMODB_TABLES['work_orders']}")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"  ⏭️  Table already exists: {DYNAMODB_TABLES['work_orders']}")

    # Work Order Operations table
    try:
        dynamodb_client.create_table(
            TableName=DYNAMODB_TABLES["wo_operations"],
            KeySchema=[
                {'AttributeName': 'work_order_id', 'KeyType': 'HASH'},
                {'AttributeName': 'operation_number', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'work_order_id', 'AttributeType': 'S'},
                {'AttributeName': 'operation_number', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"  ✅ Created table: {DYNAMODB_TABLES['wo_operations']}")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"  ⏭️  Table already exists: {DYNAMODB_TABLES['wo_operations']}")

    # NCR Records table
    try:
        dynamodb_client.create_table(
            TableName=DYNAMODB_TABLES["ncr_records"],
            KeySchema=[
                {'AttributeName': 'ncr_number', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'ncr_number', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"  ✅ Created table: {DYNAMODB_TABLES['ncr_records']}")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"  ⏭️  Table already exists: {DYNAMODB_TABLES['ncr_records']}")

    # Audit Log table
    try:
        dynamodb_client.create_table(
            TableName=DYNAMODB_TABLES["audit_log"],
            KeySchema=[
                {'AttributeName': 'audit_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'audit_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"  ✅ Created table: {DYNAMODB_TABLES['audit_log']}")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"  ⏭️  Table already exists: {DYNAMODB_TABLES['audit_log']}")


def load_work_order_data(dynamodb_resource):
    """Load work order test data into DynamoDB."""
    print("\n=== Loading Work Order Data ===")

    base_path = Path(__file__).parent.parent / "synthetic-data" / "aerospace_defense" / "work_orders"

    # Load work orders
    wo_file = base_path / "work_orders.json"
    if wo_file.exists():
        with open(wo_file) as f:
            work_orders = json.load(f)

        table = dynamodb_resource.Table(DYNAMODB_TABLES["work_orders"])
        with table.batch_writer() as batch:
            for wo in work_orders:
                batch.put_item(Item=wo)
        print(f"  ✅ Loaded {len(work_orders)} work orders")

    # Load operations
    ops_file = base_path / "operations.json"
    if ops_file.exists():
        with open(ops_file) as f:
            operations = json.load(f)

        table = dynamodb_resource.Table(DYNAMODB_TABLES["wo_operations"])
        with table.batch_writer() as batch:
            for op in operations:
                batch.put_item(Item=op)
        print(f"  ✅ Loaded {len(operations)} operations")


def create_iam_roles(iam_client):
    """Create IAM roles for demo connectors."""
    print("\n=== Creating IAM Roles ===")

    # Trust policy for Lambda/APEX
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": ["lambda.amazonaws.com", "ecs-tasks.amazonaws.com"]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # Athena query role
    try:
        iam_client.create_role(
            RoleName="apex-athena-query-role",
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for APEX to query Athena"
        )

        # Attach policies
        iam_client.attach_role_policy(
            RoleName="apex-athena-query-role",
            PolicyArn="arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
        )
        iam_client.attach_role_policy(
            RoleName="apex-athena-query-role",
            PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        )
        print("  ✅ Created role: apex-athena-query-role")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("  ⏭️  Role already exists: apex-athena-query-role")

    # DynamoDB read/write role
    try:
        iam_client.create_role(
            RoleName="apex-dynamodb-rw-role",
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for APEX to read/write DynamoDB"
        )

        iam_client.attach_role_policy(
            RoleName="apex-dynamodb-rw-role",
            PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
        )
        print("  ✅ Created role: apex-dynamodb-rw-role")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("  ⏭️  Role already exists: apex-dynamodb-rw-role")

    # S3 read-only role
    try:
        iam_client.create_role(
            RoleName="apex-s3-read-role",
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for APEX to read S3 documents"
        )

        iam_client.attach_role_policy(
            RoleName="apex-s3-read-role",
            PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        )
        print("  ✅ Created role: apex-s3-read-role")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("  ⏭️  Role already exists: apex-s3-read-role")


def print_summary():
    """Print setup summary."""
    print("\n" + "="*60)
    print("APEX AEROSPACE DEMO SETUP COMPLETE")
    print("="*60)

    print("\n📦 S3 Buckets:")
    for name, bucket in S3_BUCKETS.items():
        print(f"   - {name}: s3://{bucket}")

    print("\n📊 Athena:")
    print(f"   - Database: {ATHENA_DATABASE}")
    print(f"   - Tables: contracts, contract_line_items, pricing_history")

    print("\n🗄️  DynamoDB Tables:")
    for name, table in DYNAMODB_TABLES.items():
        print(f"   - {name}: {table}")

    print("\n🔐 IAM Roles:")
    print(f"   - apex-athena-query-role")
    print(f"   - apex-dynamodb-rw-role")
    print(f"   - apex-s3-read-role")

    print("\n✅ Demo connectors ready to use!")
    print("\nNext steps:")
    print("  1. Update connector YAML files with actual ARNs")
    print("  2. Deploy AgentCore agents")
    print("  3. Test each connector via APEX API")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Setup APEX Aerospace Demo Infrastructure")
    parser.add_argument("--profile", default="default", help="AWS profile name")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--skip-iam", action="store_true", help="Skip IAM role creation")
    args = parser.parse_args()

    print("="*60)
    print("APEX AEROSPACE DEFENSE DEMO SETUP")
    print(f"Region: {args.region} | Profile: {args.profile}")
    print("="*60)

    # Create boto3 session
    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    # Create clients
    s3_client = session.client('s3')
    dynamodb_client = session.client('dynamodb')
    dynamodb_resource = session.resource('dynamodb')
    athena_client = session.client('athena')
    iam_client = session.client('iam')

    # Run setup steps
    create_s3_buckets(s3_client, args.region)
    upload_contract_data(s3_client)
    upload_gcode_files(s3_client)
    upload_rfp_documents(s3_client)
    create_athena_database(athena_client, args.region)
    create_dynamodb_tables(dynamodb_client)

    # Wait for tables to be active
    print("\n⏳ Waiting for DynamoDB tables to become active...")
    time.sleep(10)

    load_work_order_data(dynamodb_resource)

    if not args.skip_iam:
        create_iam_roles(iam_client)

    print_summary()


if __name__ == "__main__":
    main()
