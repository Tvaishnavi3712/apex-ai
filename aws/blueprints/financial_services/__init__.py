# CBTS Apex AI Platform - Financial Services Blueprints
# BDA Blueprint definitions for document extraction

import json
import os
from typing import Dict, Any

BLUEPRINT_DIR = os.path.dirname(__file__)

BLUEPRINTS = {
    "invoice": {
        "file": "invoice_blueprint.json",
        "name": "apex-invoice-v1",
        "description": "Extract structured data from vendor invoices",
        "document_type": "invoice"
    },
    "bank_statement": {
        "file": "bank_statement_blueprint.json",
        "name": "apex-bank-statement-v1",
        "description": "Extract structured data from bank statements",
        "document_type": "bank_statement"
    },
    "contract": {
        "file": "contract_blueprint.json",
        "name": "apex-contract-v1",
        "description": "Extract structured data from business contracts",
        "document_type": "contract"
    },
    "receipt": {
        "file": "receipt_blueprint.json",
        "name": "apex-receipt-v1",
        "description": "Extract structured data from receipts",
        "document_type": "receipt"
    },
    "w9": {
        "file": "w9_blueprint.json",
        "name": "apex-w9-v1",
        "description": "Extract structured data from IRS W-9 forms",
        "document_type": "w9_form"
    }
}


def load_blueprint(blueprint_id: str) -> Dict[str, Any]:
    """Load a blueprint definition by ID"""
    if blueprint_id not in BLUEPRINTS:
        raise ValueError(f"Unknown blueprint: {blueprint_id}")

    blueprint_info = BLUEPRINTS[blueprint_id]
    filepath = os.path.join(BLUEPRINT_DIR, blueprint_info["file"])

    with open(filepath, "r") as f:
        return json.load(f)


def get_blueprint_schema(blueprint_id: str) -> Dict[str, Any]:
    """Get just the schema portion of a blueprint"""
    blueprint = load_blueprint(blueprint_id)
    return blueprint.get("schema", {})


def list_blueprints() -> Dict[str, Dict[str, str]]:
    """List all available blueprints"""
    return {
        bid: {
            "name": info["name"],
            "description": info["description"],
            "document_type": info["document_type"]
        }
        for bid, info in BLUEPRINTS.items()
    }
