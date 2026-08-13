"""
Retail Actions
Actions for receipt processing, returns, and fraud detection
"""

from .receipt_validate.handler import receipt_validate, ReceiptValidateAction
from .return_policy.handler import return_policy_check, ReturnPolicyAction
from .fraud_score.handler import fraud_score, FraudScoreAction
from .inventory_update.handler import inventory_update, InventoryUpdateAction
from .refund_process.handler import refund_process, RefundProcessAction

__all__ = [
    'receipt_validate',
    'ReceiptValidateAction',
    'return_policy_check',
    'ReturnPolicyAction',
    'fraud_score',
    'FraudScoreAction',
    'inventory_update',
    'InventoryUpdateAction',
    'refund_process',
    'RefundProcessAction'
]
