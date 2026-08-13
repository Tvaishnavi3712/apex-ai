"""
Insurance Underwriting Actions
Actions for risk assessment, premium calculation, and underwriting decisions
"""

from .risk_score.handler import risk_score, RiskScoreAction
from .premium_calculate.handler import premium_calculate, PremiumCalculateAction
from .coverage_validate.handler import coverage_validate, CoverageValidateAction
from .loss_history.handler import loss_history_check, LossHistoryAction
from .auto_decision.handler import auto_decision, AutoDecisionAction

__all__ = [
    'risk_score',
    'RiskScoreAction',
    'premium_calculate',
    'PremiumCalculateAction',
    'coverage_validate',
    'CoverageValidateAction',
    'loss_history_check',
    'LossHistoryAction',
    'auto_decision',
    'AutoDecisionAction'
]
