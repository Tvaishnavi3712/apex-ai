# Skill: Create Action Handler

When asked to create a new Lambda action handler:

## Action Handler Structure
```python
"""
{Action Name} - {Brief description}
Part of {Industry} action pack
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

# Import Apex Action SDK
import sys
sys.path.append('/opt/python')
from sdk.apex_action import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class {ActionName}Input(ActionInputSchema):
    """{Action} input schema"""
    {field_name}: {type}  # {description}


class {ActionName}Output(ActionOutputSchema):
    """{Action} output schema"""
    {field_name}: {type}


@apex_action(
    name="{action_name}",
    description="{Description of what this action does}",
    version="1.0.0",
    industry="{industry}",
    input_schema={ActionName}Input,
    output_schema={ActionName}Output
)
def {function_name}({parameters}) -> Dict[str, Any]:
    """
    {Detailed description}

    Args:
        {param}: {description}

    Returns:
        Dict containing {output description}
    """
    logger.info(f"Processing {action_name}: {parameters}")

    try:
        # Implementation logic here
        result = {
            "status": "success",
            # Add output fields
        }

        logger.info(f"{Action} completed: {result}")
        return result

    except Exception as e:
        logger.error(f"{Action} failed: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e)
        }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler entry point"""
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        result = {function_name}(**body)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## Location
Save actions to: `actions/{industry}/{action_name}/handler.py`

## Naming Conventions
- **Function name:** snake_case (e.g., `claims_adjudication`)
- **Class name:** PascalCase (e.g., `ClaimsAdjudicationInput`)
- **Action ID:** snake_case (e.g., `claims_adjudication`)

## Required Imports
```python
from sdk.apex_action import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema
```

## Common Field Types
- `str` - Text fields
- `int` - Integer numbers
- `float` - Decimal numbers
- `bool` - True/False
- `datetime` - Date/time values
- `List[str]` - List of strings
- `Dict[str, Any]` - Dictionary/object
- `Optional[str]` - Optional field
