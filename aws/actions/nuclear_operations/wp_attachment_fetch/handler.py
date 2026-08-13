"""
wp_attachment_fetch — return metadata + (synthetic) S3 URL for a work-package PDF.

In production this resolves the FileNet object id for a work-order's scanned
PDF and returns a presigned S3 URL. For the demo, the WO's PDF either exists
in `synthetic-data/nuclear_operations/work_packages/` (when reportlab was
available during generate.py) or we synthesize a deterministic S3 URL pointing
at where the file would live. Either way the chat UI can render a link.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_work_orders, data_path, not_found_envelope, missing_data_envelope,
)

# The S3 bucket the production pipeline lands FileNet exports into. Override
# via env var for non-prod accounts.
import os
S3_BUCKET = os.environ.get("APEX_STP_WP_BUCKET", "apex-stp-work-packages")
S3_REGION = os.environ.get("APEX_STP_WP_REGION", "us-east-1")


@apex_action(ApexActionSchema(
    name="wp_attachment_fetch",
    description="Return work-package PDF metadata + S3 URL for a given work order id (FileNet proxy).",
    category="document_fetch",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Attachment fetch request")
        .add_string("wo_id", "Work order id, e.g. WO-2026-00871", required=True),
    output_schema=ActionOutputSchema(description="WP attachment envelope")
        .add_string("status", "ok | error | not_found")
        .add_string("wo_id", "Work order id")
        .add_string("pdf_path", "Local path (when synthetic PDF exists)")
        .add_string("s3_url", "Presigned-style S3 URL")
        .add_number("page_count", "PDF page count (estimated)")
        .add_string("cover_sheet_data", "Cover sheet summary {wo_id, equipment_id, technicians, sign_off_status}")
        .add_number("procedure_steps_count", "Number of procedure steps in the WP"),
))
def wp_attachment_fetch(wo_id: str) -> dict:
    """Return PDF metadata + URL for a work order's package."""
    if not wo_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "wo_id is required"}

    work_orders = load_work_orders()
    if work_orders is None:
        return missing_data_envelope("work_orders.json")

    wo = next((w for w in work_orders if w.get("wo_id") == wo_id), None)
    if wo is None:
        return not_found_envelope("work_order", wo_id)

    # Local PDF — try the hand-curated hero PDFs first, fall back to the
    # bulk wp_*.pdf naming convention.
    hero_pdf = data_path("pdfs", f"{wo_id}_work_package.pdf")
    bulk_pdf = data_path("work_packages", f"wp_{wo_id}.pdf")
    local_pdf = hero_pdf if hero_pdf.exists() else bulk_pdf

    # When the local PDF exists, expose it via the backend's static-files
    # endpoint so the chat UI can render the citation. Otherwise fall back
    # to the synthetic S3 URL the production pipeline would land at.
    if local_pdf.exists():
        s3_url = f"/api/v1/documents/stp/{local_pdf.name}"
    else:
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/work_packages/wp_{wo_id}.pdf"

    return {
        "status": "ok",
        "wo_id": wo_id,
        "pdf_path": str(local_pdf) if local_pdf.exists() else None,
        "s3_url": s3_url,
        "page_count": 6,  # typical WP cover + 5 step pages — synthetic constant
        "cover_sheet_data": {
            "wo_id": wo_id,
            "equipment_id": wo.get("equipment_id"),
            "type": wo.get("type"),
            "technicians": wo.get("technician_ids", []),
            "sign_off_status": "signed" if wo.get("status") == "closed" else "pending",
            "opened": wo.get("opened"),
            "closed": wo.get("closed"),
            "narrative": (wo.get("narrative") or "")[:200],
        },
        "procedure_steps_count": 5,
    }


def handler(event, context=None):
    return wp_attachment_fetch(wo_id=event.get("wo_id", ""))
