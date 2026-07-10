"""
Decorators for creating Apex Actions
Inspired by Sema4.ai's action decorators but designed for AgentCore Gateway
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps
import inspect
import json

from .schemas import ActionInputSchema, ActionOutputSchema


@dataclass
class ApexActionSchema:
    """
    Schema definition for an Apex Action

    Example:
        @apex_action(ApexActionSchema(
            name="vendor_lookup",
            description="Check if vendor exists in approved vendor list",
            category="data_lookup",
            industry="financial_services",
            input_schema=ActionInputSchema()
                .add_string("vendor_name", "Name of the vendor", required=True),
            output_schema=ActionOutputSchema()
                .add_boolean("exists", "Whether vendor was found")
                .add_string("vendor_id", "Vendor ID if found")
        ))
        def vendor_lookup(vendor_name: str) -> dict:
            # Implementation
            pass
    """
    name: str
    description: str
    input_schema: ActionInputSchema
    output_schema: Optional[ActionOutputSchema] = None
    category: str = "business_logic"
    industry: str = "general"
    version: str = "1.0"
    tags: Optional[list] = None

    def to_gateway_schema(self) -> Dict[str, Any]:
        """Convert to AgentCore Gateway tool schema format"""
        schema = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema.to_dict()
        }

        if self.output_schema:
            schema["outputSchema"] = self.output_schema.to_dict()

        return schema

    def to_registry_format(self) -> Dict[str, Any]:
        """Convert to format for storing in action registry"""
        return {
            "action_id": self.name,
            "name": self.name,
            "display_name": self.name.replace("_", " ").title(),
            "description": self.description,
            "category": self.category,
            "industry": self.industry,
            "version": self.version,
            "type": "lambda",
            "input_schema": self.input_schema.to_dict(),
            "output_schema": self.output_schema.to_dict() if self.output_schema else None,
            "tags": self.tags or []
        }


def apex_action(schema: ApexActionSchema):
    """
    Decorator to mark a function as an Apex Action

    The decorated function will have metadata attached for:
    - Registration with AgentCore Gateway
    - Schema validation
    - Documentation generation

    Example:
        @apex_action(ApexActionSchema(
            name="calculate_tax",
            description="Calculate tax for an amount",
            input_schema=ActionInputSchema()
                .add_number("amount", "Amount to calculate tax on", required=True)
                .add_number("rate", "Tax rate as decimal", required=True),
            output_schema=ActionOutputSchema()
                .add_number("tax", "Calculated tax amount")
                .add_number("total", "Total including tax")
        ))
        def calculate_tax(amount: float, rate: float) -> dict:
            tax = amount * rate
            return {
                "tax": tax,
                "total": amount + tax
            }
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For Lambda handler, the event is the first arg
            if args and isinstance(args[0], dict):
                event = args[0]
                context = args[1] if len(args) > 1 else None

                # Extract parameters from event
                try:
                    result = func(**event)
                except TypeError:
                    # Function might expect positional args
                    result = func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            return result

        # Attach metadata to the function
        wrapper._apex_action = True
        wrapper._apex_schema = schema
        wrapper._apex_name = schema.name
        wrapper._apex_description = schema.description

        # For discovery
        wrapper.get_schema = lambda: schema
        wrapper.get_gateway_schema = lambda: schema.to_gateway_schema()
        wrapper.get_registry_format = lambda: schema.to_registry_format()

        return wrapper

    return decorator


def create_lambda_handler(action_func: Callable) -> Callable:
    """
    Create a Lambda handler from an Apex Action function

    This wraps the action function to handle:
    - AgentCore Gateway context extraction
    - Error handling
    - Response formatting

    Example:
        @apex_action(...)
        def my_action(param1: str) -> dict:
            return {"result": param1}

        # In Lambda
        handler = create_lambda_handler(my_action)
    """
    def handler(event, context):
        try:
            # Extract tool context from AgentCore Gateway
            tool_context = {}
            if hasattr(context, 'client_context') and context.client_context:
                tool_context = context.client_context.custom or {}

            # Log for debugging
            print(f"Action: {getattr(action_func, '_apex_name', 'unknown')}")
            print(f"Event: {json.dumps(event)}")
            print(f"Tool context: {tool_context}")

            # Execute the action
            result = action_func(**event)

            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {"result": result}

            return result

        except Exception as e:
            print(f"Error in action: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "action": getattr(action_func, '_apex_name', 'unknown')
            }

    # Copy metadata
    handler._apex_action = getattr(action_func, '_apex_action', False)
    handler._apex_schema = getattr(action_func, '_apex_schema', None)

    return handler


def discover_actions(module) -> list:
    """
    Discover all Apex Actions in a module

    Example:
        import my_actions
        actions = discover_actions(my_actions)
        for action in actions:
            print(f"Found action: {action._apex_name}")
    """
    actions = []

    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and hasattr(obj, '_apex_action') and obj._apex_action:
            actions.append(obj)

    return actions
