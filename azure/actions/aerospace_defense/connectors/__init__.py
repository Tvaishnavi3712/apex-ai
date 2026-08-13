"""
APEX Aerospace & Defense Data Connectors

AWS-based connectors that replace client systems for demo purposes:
- PowerFlow SQL → Athena + S3 (contracts, pricing)
- GovCloud ERP → Cosmos DB (work orders, NCRs)
- SolidWorks PDM → S3 (CAD drawings, G-code)
- SharePoint GCC High → S3 (ITAR documents)

All connectors support:
- ITAR compliance
- NIST 800-171 audit logging
- READ/WRITE mode indicators
"""

from .athena_connector import (
    query_contracts,
    get_pricing_history,
    get_contract_line_items
)

from .cosmos_db_connector import (
    query_work_order,
    list_work_orders,
    update_work_order_status,
    create_work_order,
    create_ncr
)

from .s3_document_connector import (
    get_drawing,
    list_revisions,
    get_gcode_program,
    list_gcode_programs,
    get_work_instruction,
    get_rfp_document,
    list_program_documents
)

__all__ = [
    # Athena (PowerFlow replacement)
    "query_contracts",
    "get_pricing_history",
    "get_contract_line_items",

    # Cosmos DB (ERP replacement)
    "query_work_order",
    "list_work_orders",
    "update_work_order_status",
    "create_work_order",
    "create_ncr",

    # S3 Documents (PDM + SharePoint replacement)
    "get_drawing",
    "list_revisions",
    "get_gcode_program",
    "list_gcode_programs",
    "get_work_instruction",
    "get_rfp_document",
    "list_program_documents"
]
