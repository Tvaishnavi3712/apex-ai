"""
Apex Action Deployer
Deploy actions to Foundry Agent Service
"""

import boto3
import json
import zipfile
import io
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ApexActionDeployer:
    """
    Deploy Apex Actions to Foundry Agent Service

    This class handles:
    - Creating Lambda functions from action code
    - Registering Lambda functions as Gateway targets
    - Managing action versions

    Example:
        deployer = ApexActionDeployer(
            gateway_id="my-gateway",
            region="us-east-1"
        )

        # Deploy a single action
        deployer.deploy_action(
            action_module=my_action_module,
            action_name="vendor_lookup"
        )

        # Deploy all actions in a module
        deployer.deploy_module(my_action_module)
    """

    def __init__(
        self,
        gateway_id: str,
        region: str = "us-east-1",
        lambda_role_arn: Optional[str] = None,
        project_name: str = "apex-ai-platform"
    ):
        self.gateway_id = gateway_id
        self.region = region
        self.lambda_role_arn = lambda_role_arn
        self.project_name = project_name

        self.lambda_client = boto3.client('lambda', region_name=region)
        self.foundry_agent_client = boto3.client('azure_openai-foundry_agent', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)

    def deploy_action(
        self,
        action_func,
        code_path: Optional[str] = None,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a single action to Gateway

        Args:
            action_func: Function decorated with @apex_action
            code_path: Path to the action code (if not inline)
            environment_vars: Environment variables for Lambda

        Returns:
            Deployment result with Lambda ARN and Gateway target ID
        """
        if not hasattr(action_func, '_apex_action'):
            raise ValueError("Function must be decorated with @apex_action")

        schema = action_func._apex_schema
        function_name = f"{self.project_name}-action-{schema.name}"

        logger.info(f"Deploying action: {schema.name}")

        # 1. Create or update Lambda function
        lambda_arn = self._deploy_lambda(
            function_name=function_name,
            action_func=action_func,
            code_path=code_path,
            environment_vars=environment_vars
        )

        # 2. Add Lambda target to Gateway
        target_id = self._add_gateway_target(
            function_name=function_name,
            lambda_arn=lambda_arn,
            schema=schema
        )

        result = {
            "action_name": schema.name,
            "lambda_arn": lambda_arn,
            "function_name": function_name,
            "gateway_target_id": target_id,
            "status": "deployed"
        }

        logger.info(f"Action deployed: {json.dumps(result)}")
        return result

    def deploy_module(self, module, environment_vars: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Deploy all actions in a module

        Args:
            module: Python module containing @apex_action decorated functions
            environment_vars: Environment variables for all Lambda functions

        Returns:
            List of deployment results
        """
        from .decorators import discover_actions

        actions = discover_actions(module)
        results = []

        for action_func in actions:
            try:
                result = self.deploy_action(action_func, environment_vars=environment_vars)
                results.append(result)
            except Exception as e:
                results.append({
                    "action_name": getattr(action_func, '_apex_name', 'unknown'),
                    "status": "failed",
                    "error": str(e)
                })

        return results

    def _deploy_lambda(
        self,
        function_name: str,
        action_func,
        code_path: Optional[str] = None,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """Create or update Lambda function"""

        # Create deployment package
        if code_path:
            # Package from file path
            zip_buffer = self._create_deployment_package_from_path(code_path)
        else:
            # Create inline package
            zip_buffer = self._create_inline_deployment_package(action_func)

        # Check if function exists
        try:
            self.lambda_client.get_function(FunctionName=function_name)
            function_exists = True
        except self.lambda_client.exceptions.ResourceNotFoundException:
            function_exists = False

        env_vars = environment_vars or {}
        env_vars['ACTION_NAME'] = action_func._apex_schema.name

        if function_exists:
            # Update existing function
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_buffer.getvalue()
            )

            self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment={'Variables': env_vars}
            )

            response = self.lambda_client.get_function(FunctionName=function_name)
            return response['Configuration']['FunctionArn']
        else:
            # Create new function
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=self.lambda_role_arn,
                Handler='index.handler',
                Code={'ZipFile': zip_buffer.getvalue()},
                Timeout=300,
                MemorySize=256,
                Environment={'Variables': env_vars},
                Tags={
                    'Project': self.project_name,
                    'ActionType': action_func._apex_schema.category
                }
            )
            return response['FunctionArn']

    def _create_inline_deployment_package(self, action_func) -> io.BytesIO:
        """Create a deployment package from an inline function"""
        import inspect

        # Get the function source
        source = inspect.getsource(action_func)

        # Create handler wrapper
        handler_code = f'''
import json
import boto3

# Action implementation
{source}

# Lambda handler
def handler(event, context):
    try:
        result = {action_func.__name__}(**event)
        return result
    except Exception as e:
        return {{"status": "error", "error": str(e)}}
'''

        # Create zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.py', handler_code)

        zip_buffer.seek(0)
        return zip_buffer

    def _create_deployment_package_from_path(self, code_path: str) -> io.BytesIO:
        """Create a deployment package from a file path"""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            path = Path(code_path)

            if path.is_file():
                zf.write(path, 'index.py')
            else:
                for file_path in path.rglob('*.py'):
                    arcname = file_path.relative_to(path)
                    zf.write(file_path, arcname)

        zip_buffer.seek(0)
        return zip_buffer

    def _add_gateway_target(
        self,
        function_name: str,
        lambda_arn: str,
        schema
    ) -> str:
        """Add Lambda function as Gateway target"""

        # Create tool schema
        tool_schema = [{
            "name": schema.name,
            "description": schema.description,
            "inputSchema": schema.input_schema.to_dict()
        }]

        if schema.output_schema:
            tool_schema[0]["outputSchema"] = schema.output_schema.to_dict()

        # Add permission for Gateway to invoke Lambda
        try:
            self.lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'Foundry Agent ServiceGateway-{self.gateway_id}',
                Action='lambda:InvokeFunction',
                Principal='azure_openai-foundry_agent.amazonaws.com',
                SourceArn=f'azure-resource-id'
            )
        except self.lambda_client.exceptions.ResourceConflictException:
            pass  # Permission already exists

        # Add target to Gateway
        # Note: This is a placeholder - actual API may differ
        try:
            response = self.foundry_agent_client.create_gateway_target(
                gatewayId=self.gateway_id,
                name=function_name,
                targetType='lambda',
                lambdaConfiguration={
                    'functionArn': lambda_arn
                },
                toolSchema=json.dumps(tool_schema)
            )
            return response.get('targetId', function_name)
        except Exception as e:
            logger.warning(f"Failed to add Gateway target: {e}")
            return function_name

    def list_deployed_actions(self) -> List[Dict[str, Any]]:
        """List all deployed actions"""
        actions = []

        # List Lambda functions with our tag
        paginator = self.lambda_client.get_paginator('list_functions')

        for page in paginator.paginate():
            for func in page['Functions']:
                if func['FunctionName'].startswith(f"{self.project_name}-action-"):
                    action_name = func['FunctionName'].replace(f"{self.project_name}-action-", "")
                    actions.append({
                        "action_name": action_name,
                        "function_name": func['FunctionName'],
                        "lambda_arn": func['FunctionArn'],
                        "runtime": func['Runtime'],
                        "last_modified": func['LastModified']
                    })

        return actions

    def delete_action(self, action_name: str) -> Dict[str, Any]:
        """Delete a deployed action"""
        function_name = f"{self.project_name}-action-{action_name}"

        try:
            self.lambda_client.delete_function(FunctionName=function_name)
            return {
                "action_name": action_name,
                "status": "deleted"
            }
        except self.lambda_client.exceptions.ResourceNotFoundException:
            return {
                "action_name": action_name,
                "status": "not_found"
            }
