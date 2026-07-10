"""
Manufacturing Industry Actions
Actions for purchase order processing, shipping, and quality control
"""

from .inventory_lookup.handler import inventory_lookup, InventoryLookupAction
from .carrier_validation.handler import carrier_validation, CarrierValidationAction
from .quality_threshold.handler import quality_threshold, QualityThresholdAction

__all__ = [
    'inventory_lookup',
    'InventoryLookupAction',
    'carrier_validation',
    'CarrierValidationAction',
    'quality_threshold',
    'QualityThresholdAction',
]
