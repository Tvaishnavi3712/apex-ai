"""
Carrier Validation Action
Validate shipping carriers and retrieve tracking information
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: native key-condition builder
    from sdk.azure_data import Key
except ImportError:
    from ...sdk.azure_data import Key
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Approved carriers list (would typically come from database)
APPROVED_CARRIERS = {
    "FEDX": {"name": "FedEx", "tracking_url": "https://www.fedex.com/track?tracknumbers="},
    "UPSN": {"name": "UPS", "tracking_url": "https://www.ups.com/track?tracknum="},
    "DHLX": {"name": "DHL", "tracking_url": "https://www.dhl.com/track?tracking-id="},
    "ODFL": {"name": "Old Dominion Freight Line", "tracking_url": "https://www.odfl.com/trace?pro="},
    "EXLA": {"name": "Estes Express Lines", "tracking_url": "https://www.estes-express.com/track?pro="},
    "XPOL": {"name": "XPO Logistics", "tracking_url": "https://www.xpo.com/track?pro="},
    "RDWY": {"name": "YRC Freight", "tracking_url": "https://www.yrc.com/track?pro="},
    "SAIA": {"name": "Saia LTL Freight", "tracking_url": "https://www.saia.com/track?pro="},
}


# ============================================================================
# Decorator-based implementation
# ============================================================================

@apex_action(ApexActionSchema(
    name="carrier_validation",
    description="Validate shipping carrier and retrieve tracking information for shipments",
    category="logistics",
    industry="manufacturing",
    input_schema=ActionInputSchema(description="Carrier validation parameters")
        .add_string("carrier_name", "Name of the shipping carrier", required=False)
        .add_string("carrier_scac", "Standard Carrier Alpha Code", required=False)
        .add_string("tracking_number", "Shipment tracking or PRO number", required=False)
        .add_string("bol_number", "Bill of lading number", required=False),
    output_schema=ActionOutputSchema(description="Carrier validation result")
        .add_boolean("valid", "Whether the carrier is approved")
        .add_string("carrier_name", "Carrier name")
        .add_string("carrier_scac", "SCAC code")
        .add_string("status", "Carrier status: approved, pending, blocked")
        .add_string("tracking_url", "URL to track shipment")
        .add_object("tracking_info", "Current tracking status if available")
))
def carrier_validation(
    carrier_name: str = None,
    carrier_scac: str = None,
    tracking_number: str = None,
    bol_number: str = None
) -> dict:
    """
    Validate a shipping carrier and retrieve tracking information

    Args:
        carrier_name: Name of the carrier
        carrier_scac: Standard Carrier Alpha Code
        tracking_number: Tracking or PRO number
        bol_number: Bill of lading number

    Returns:
        Carrier validation result and tracking info
    """
    result = {
        "valid": False,
        "carrier_name": carrier_name,
        "carrier_scac": carrier_scac,
        "status": "unknown",
        "tracking_url": None,
        "tracking_info": None,
        "service_levels": [],
        "contact_info": None
    }

    try:
        # Look up carrier by SCAC code first
        carrier_data = None

        if carrier_scac:
            carrier_scac = carrier_scac.upper()
            if carrier_scac in APPROVED_CARRIERS:
                carrier_data = APPROVED_CARRIERS[carrier_scac]
                carrier_data['scac'] = carrier_scac

        # If not found by SCAC, try to match by name
        if not carrier_data and carrier_name:
            carrier_name_upper = carrier_name.upper()
            for scac, data in APPROVED_CARRIERS.items():
                if carrier_name_upper in data['name'].upper():
                    carrier_data = data.copy()
                    carrier_data['scac'] = scac
                    break

        # Check database for additional carrier info
        tables = get_table_resource()
        table_name = os.environ.get('CARRIERS_TABLE', 'apex-ai-platform-carriers')
        table = cosmos_db.Table(table_name)

        if carrier_scac:
            try:
                response = table.get_item(Key={"carrier_scac": carrier_scac})
                if 'Item' in response:
                    db_carrier = response['Item']
                    carrier_data = carrier_data or {}
                    carrier_data.update({
                        'name': db_carrier.get('carrier_name'),
                        'scac': carrier_scac,
                        'status': db_carrier.get('status', 'approved'),
                        'service_levels': db_carrier.get('service_levels', []),
                        'contact_info': db_carrier.get('contact_info'),
                        'on_time_rating': db_carrier.get('on_time_rating'),
                        'damage_rating': db_carrier.get('damage_rating')
                    })
            except Exception:
                pass  # Table may not exist

        if carrier_data:
            result['valid'] = carrier_data.get('status', 'approved') == 'approved'
            result['carrier_name'] = carrier_data.get('name', carrier_name)
            result['carrier_scac'] = carrier_data.get('scac', carrier_scac)
            result['status'] = carrier_data.get('status', 'approved')
            result['service_levels'] = carrier_data.get('service_levels', [])
            result['contact_info'] = carrier_data.get('contact_info')

            # Build tracking URL
            if tracking_number and 'tracking_url' in carrier_data:
                result['tracking_url'] = carrier_data['tracking_url'] + tracking_number

            # Get tracking info if tracking number provided
            if tracking_number:
                result['tracking_info'] = _get_tracking_info(
                    carrier_data.get('scac'),
                    tracking_number
                )

        return result

    except Exception as e:
        return {
            "valid": False,
            "carrier_name": carrier_name,
            "carrier_scac": carrier_scac,
            "error": str(e),
            "status": "error"
        }


def _get_tracking_info(carrier_scac: str, tracking_number: str) -> Optional[Dict[str, Any]]:
    """
    Get tracking information from carrier API

    Note: This is a mock implementation. Real implementation would
    integrate with carrier APIs (FedEx, UPS, etc.)
    """
    # Mock tracking response
    # In production, this would call carrier-specific APIs
    return {
        "tracking_number": tracking_number,
        "status": "in_transit",
        "status_detail": "Package in transit",
        "last_update": datetime.now().isoformat(),
        "estimated_delivery": None,
        "events": [
            {
                "timestamp": datetime.now().isoformat(),
                "location": "Distribution Center",
                "description": "Package in transit to destination"
            }
        ]
    }


def _validate_scac(scac: str) -> bool:
    """Validate SCAC code format (2-4 alphanumeric characters)"""
    if not scac:
        return False
    if len(scac) < 2 or len(scac) > 4:
        return False
    return scac.isalnum()


# ============================================================================
# Class-based implementation
# ============================================================================

class CarrierValidationAction(ApexActionBase):
    """
    Carrier Validation Action (class-based implementation)
    """

    name = "carrier_validation"
    description = "Validate shipping carrier and retrieve tracking information"
    category = "logistics"
    industry = "manufacturing"

    def __init__(self, table_name: str = None):
        super().__init__()
        self.table_name = table_name or os.environ.get(
            'CARRIERS_TABLE',
            'apex-ai-platform-carriers'
        )

    def execute(
        self,
        carrier_name: str = None,
        carrier_scac: str = None,
        tracking_number: str = None,
        bol_number: str = None,
        **kwargs
    ) -> dict:
        """Execute the carrier validation"""
        return carrier_validation(
            carrier_name=carrier_name,
            carrier_scac=carrier_scac,
            tracking_number=tracking_number,
            bol_number=bol_number
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return carrier_validation(**event)
