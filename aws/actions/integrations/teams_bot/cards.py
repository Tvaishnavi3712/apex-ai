"""
Microsoft Teams Adaptive Card Builders
Templates for various notification and interaction cards.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def build_status_card(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Build status card for a document."""

    status_colors = {
        "completed": "good",
        "processing": "warning",
        "pending_approval": "accent",
        "exception": "warning",
        "failed": "attention"
    }

    status_icons = {
        "completed": "✅",
        "processing": "⏳",
        "pending_approval": "🔔",
        "exception": "⚠️",
        "failed": "❌"
    }

    status = doc.get("status", "unknown")

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": f"📄 {doc.get('document_type', 'Document')} {doc.get('document_id', '')}"
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": f"{status_icons.get(status, '📋')} {status.replace('_', ' ').title()}",
                                "color": status_colors.get(status, "default"),
                                "weight": "Bolder"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Document ID", "value": doc.get("document_id", "N/A")},
                    {"title": "Type", "value": doc.get("document_type", "N/A")},
                    {"title": "Vendor", "value": doc.get("vendor_name", "N/A")},
                    {"title": "Amount", "value": doc.get("amount", "N/A")},
                    {"title": "Received", "value": doc.get("created_at", "N/A")},
                    {"title": "Processed", "value": doc.get("processed_at", "N/A")}
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "View in APEX",
                "url": f"https://apex.company.com/documents/{doc.get('document_id', '')}"
            },
            {
                "type": "Action.Submit",
                "title": "Refresh Status",
                "data": {
                    "action": "refresh",
                    "document_id": doc.get("document_id", "")
                }
            }
        ]
    }


def build_approval_card(
    document_id: str,
    document_type: str,
    vendor: str,
    amount: str,
    reason: str,
    requested_by: str = None,
    wait_time: str = None
) -> Dict[str, Any]:
    """Build approval request card."""

    facts = [
        {"title": "Document", "value": document_id},
        {"title": "Type", "value": document_type},
        {"title": "Vendor", "value": vendor},
        {"title": "Amount", "value": amount},
        {"title": "Reason", "value": reason}
    ]

    if requested_by:
        facts.append({"title": "Requested By", "value": requested_by})

    if wait_time:
        facts.append({"title": "Waiting", "value": wait_time})

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "🔔 Approval Required",
                "color": "Accent"
            },
            {
                "type": "TextBlock",
                "text": reason,
                "wrap": True,
                "weight": "Bolder"
            },
            {
                "type": "FactSet",
                "facts": facts
            },
            {
                "type": "TextBlock",
                "text": "Please review and take action:",
                "size": "Small",
                "isSubtle": True,
                "spacing": "Medium"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "✅ Approve",
                "style": "positive",
                "data": {
                    "action": "approve",
                    "document_id": document_id
                }
            },
            {
                "type": "Action.ShowCard",
                "title": "❌ Reject",
                "card": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "Input.Text",
                            "id": "rejection_reason",
                            "placeholder": "Enter rejection reason...",
                            "isMultiline": True
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Submit Rejection",
                            "style": "destructive",
                            "data": {
                                "action": "reject",
                                "document_id": document_id
                            }
                        }
                    ]
                }
            },
            {
                "type": "Action.OpenUrl",
                "title": "📄 View Document",
                "url": f"https://apex.company.com/documents/{document_id}"
            }
        ]
    }


def build_pending_list_card(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build card showing list of pending approvals."""

    body = [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": f"🔔 You have {len(items)} pending approval(s)"
        }
    ]

    for item in items[:5]:  # Limit to 5 items
        body.append({
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"**{item.get('document_id', 'Unknown')}** | {item.get('vendor_name', 'Unknown')}",
                                    "wrap": True
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Amount: {item.get('amount', 'N/A')} | Waiting: {item.get('wait_time', 'N/A')}",
                                    "size": "Small",
                                    "isSubtle": True,
                                    "spacing": "None"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "ActionSet",
                                    "actions": [
                                        {
                                            "type": "Action.Submit",
                                            "title": "✅",
                                            "data": {
                                                "action": "approve",
                                                "document_id": item.get("document_id", "")
                                            }
                                        },
                                        {
                                            "type": "Action.Submit",
                                            "title": "❌",
                                            "data": {
                                                "action": "reject",
                                                "document_id": item.get("document_id", "")
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "separator": True
        })

    if len(items) > 5:
        body.append({
            "type": "TextBlock",
            "text": f"_...and {len(items) - 5} more_",
            "isSubtle": True,
            "size": "Small"
        })

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": body,
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "View All in APEX",
                "url": "https://apex.company.com/agent-hub"
            }
        ]
    }


def build_help_card() -> Dict[str, Any]:
    """Build help card with available commands."""

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "🤖 APEX AI Bot - Help"
            },
            {
                "type": "TextBlock",
                "text": "Here are the commands I understand:",
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "status <ID>", "value": "Check document status"},
                    {"title": "pending", "value": "View your pending approvals"},
                    {"title": "approve <ID>", "value": "Approve a document"},
                    {"title": "reject <ID> [reason]", "value": "Reject a document"},
                    {"title": "search <query>", "value": "Search for documents"},
                    {"title": "help", "value": "Show this help message"}
                ]
            },
            {
                "type": "TextBlock",
                "text": "**Examples:**",
                "weight": "Bolder",
                "spacing": "Medium"
            },
            {
                "type": "TextBlock",
                "text": "• `status INV-2024-0892`\n• `approve PO-2024-0234`\n• `search invoices from Acme`",
                "wrap": True,
                "fontType": "Monospace",
                "size": "Small"
            },
            {
                "type": "TextBlock",
                "text": "💡 **Tip:** You can also upload documents directly to this chat!",
                "wrap": True,
                "spacing": "Medium",
                "isSubtle": True
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Open APEX Platform",
                "url": "https://apex.company.com"
            }
        ]
    }


def build_error_card(title: str, message: str) -> Dict[str, Any]:
    """Build error notification card."""

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": f"❌ {title}",
                "color": "Attention"
            },
            {
                "type": "TextBlock",
                "text": message,
                "wrap": True
            }
        ]
    }


def build_success_card(title: str, message: str) -> Dict[str, Any]:
    """Build success notification card."""

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": f"✅ {title}",
                "color": "Good"
            },
            {
                "type": "TextBlock",
                "text": message,
                "wrap": True
            }
        ]
    }


def build_exception_card(
    document_id: str,
    exception_type: str,
    exception_reason: str,
    confidence_score: float = None,
    problem_fields: List[Dict] = None
) -> Dict[str, Any]:
    """Build exception alert card."""

    facts = [
        {"title": "Document", "value": document_id},
        {"title": "Exception Type", "value": exception_type},
        {"title": "Reason", "value": exception_reason}
    ]

    if confidence_score is not None:
        facts.append({
            "title": "Confidence Score",
            "value": f"{confidence_score * 100:.1f}%"
        })

    body = [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": "⚠️ Processing Exception",
            "color": "Warning"
        },
        {
            "type": "FactSet",
            "facts": facts
        }
    ]

    if problem_fields:
        body.append({
            "type": "TextBlock",
            "text": "**Problem Fields:**",
            "weight": "Bolder",
            "spacing": "Medium"
        })

        for field in problem_fields[:5]:
            body.append({
                "type": "TextBlock",
                "text": f"• `{field.get('name', 'Unknown')}`: {field.get('issue', 'Low confidence')}",
                "size": "Small",
                "spacing": "None"
            })

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": body,
        "actions": [
            {
                "type": "Action.Submit",
                "title": "🔍 Review",
                "style": "positive",
                "data": {
                    "action": "review",
                    "document_id": document_id
                }
            },
            {
                "type": "Action.Submit",
                "title": "✅ Override",
                "data": {
                    "action": "override",
                    "document_id": document_id
                }
            },
            {
                "type": "Action.Submit",
                "title": "❌ Reject",
                "style": "destructive",
                "data": {
                    "action": "reject",
                    "document_id": document_id
                }
            }
        ]
    }


def build_notification_card(
    title: str,
    message: str,
    notification_type: str = "info",
    document_id: str = None,
    fields: List[Dict] = None,
    actions: List[Dict] = None
) -> Dict[str, Any]:
    """Build a generic notification card."""

    type_config = {
        "info": {"icon": "ℹ️", "color": "Default"},
        "success": {"icon": "✅", "color": "Good"},
        "warning": {"icon": "⚠️", "color": "Warning"},
        "error": {"icon": "❌", "color": "Attention"}
    }

    config = type_config.get(notification_type, type_config["info"])

    body = [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": f"{config['icon']} {title}",
            "color": config["color"]
        },
        {
            "type": "TextBlock",
            "text": message,
            "wrap": True
        }
    ]

    if fields:
        body.append({
            "type": "FactSet",
            "facts": [
                {"title": f["label"], "value": f["value"]}
                for f in fields
            ]
        })

    card_actions = []
    if actions:
        for action in actions:
            if action.get("url"):
                card_actions.append({
                    "type": "Action.OpenUrl",
                    "title": action["label"],
                    "url": action["url"]
                })
            else:
                card_actions.append({
                    "type": "Action.Submit",
                    "title": action["label"],
                    "data": {
                        "action": action.get("action_id", "action"),
                        "document_id": document_id
                    }
                })

    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": body
    }

    if card_actions:
        card["actions"] = card_actions

    return card
