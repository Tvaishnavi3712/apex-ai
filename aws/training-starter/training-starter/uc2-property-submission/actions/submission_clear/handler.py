"""
Submission Clearance Action
Clear an inbound commercial property submission against in-force policies and
open submissions, so the same account is never worked twice by two underwriters
and the carrier never bids against itself through two brokers.

TRAINING USE CASE 2 — Insurance Underwriting.

Deploy location:  actions/insurance_underwriting/submission_clear/handler.py
Registry entry:   INDUSTRY_ACTIONS["insurance_underwriting"] += ["submission_clear"]
Resulting id:     insurance_underwriting.submission_clear

Clearance is the first gate for a reason. Everything downstream — appetite,
catastrophe aggregation, rating — is wasted work if the account is already in
the house under a different broker or a different affiliate name.
"""

import os
import re
import sys
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import (  # noqa: E402
    apex_action,
    ApexActionSchema,
    ActionInputSchema,
    ActionOutputSchema,
    ApexActionBase,
)

# A FEIN match is conclusive. Name and address matches are probable and are
# reported with confidence so a human can see why the match fired.
FEIN_MATCH_CONFIDENCE = 1.00
NAME_MATCH_FLOOR = 0.82
ADDRESS_MATCH_FLOOR = 0.88

# Corporate suffixes stripped before comparing entity names, so
# "Cedar Ridge Logistics LLC" and "CEDAR RIDGE LOGISTICS, L.L.C." collapse.
_ENTITY_SUFFIXES = (
    "INCORPORATED", "CORPORATION", "PARTNERSHIP", "COMPANY", "LIMITED",
    "HOLDINGS", "ENTERPRISES", "PROPERTIES", "GROUP", "TRUST",
    "LLC", "LLP", "LP", "LTD", "INC", "CORP", "CO", "PLC", "PC", "PA",
)


@apex_action(ApexActionSchema(
    name="submission_clear",
    description=(
        "Clear a commercial property submission against in-force policies and "
        "open submissions using FEIN, entity name, affiliate names and first "
        "location address, and classify the result as clear, renewal, broker "
        "conflict or same-broker resubmission"
    ),
    category="underwriting",
    industry="insurance_underwriting",
    version="1.0",
    tags=["clearance", "commercial_property", "broker_of_record", "deduplication"],
    input_schema=ActionInputSchema(description="Clearance inputs")
        .add_string("submission_id", "Broker submission reference", required=True)
        .add_string("named_insured", "Full legal name of the first named insured", required=True)
        .add_string("fein", "Federal employer identification number", required=False)
        .add_array("additional_named_insureds", "Affiliated entities on the submission", required=False)
        .add_array("dba_names", "Trading names on the submission", required=False)
        .add_string("first_location_address", "Street address of the first scheduled location", required=False)
        .add_string("first_location_postal_code", "Postal code of the first scheduled location", required=False)
        .add_string("broker_agency_name", "Producing broker or agency", required=False)
        .add_string("requested_effective_date", "Requested effective date, YYYY-MM-DD", required=False)
        .add_array("policy_register", "In-force policies to clear against. When omitted the action reads the policy register table", required=False)
        .add_array("open_submissions", "Open submissions to clear against. When omitted the action reads the open submissions table", required=False),
    output_schema=ActionOutputSchema(description="Clearance result")
        .add_string("clearance_status", "clear, renewal, broker_conflict, or same_broker_resubmission")
        .add_boolean("blocking_conflict", "True when the submission must not proceed to an underwriter")
        .add_array("matched_records", "Every record matched, highest confidence first")
        .add_string("controlling_broker", "Broker who currently controls the account, when one exists")
        .add_string("match_basis", "fein, entity_name, address, or none")
        .add_number("highest_confidence", "Confidence of the strongest match, 0.0 to 1.0")
        .add_string("routing_queue", "Queue this submission must go to")
        .add_string("clearance_note", "Human-readable explanation for the underwriting packet")
))
def submission_clear(
    submission_id: str,
    named_insured: str,
    fein: Optional[str] = None,
    additional_named_insureds: Optional[List[str]] = None,
    dba_names: Optional[List[str]] = None,
    first_location_address: Optional[str] = None,
    first_location_postal_code: Optional[str] = None,
    broker_agency_name: Optional[str] = None,
    requested_effective_date: Optional[str] = None,
    policy_register: Optional[List[Dict[str, Any]]] = None,
    open_submissions: Optional[List[Dict[str, Any]]] = None,
) -> dict:
    """
    Clear a submission against in-force policies and open submissions.

    Args:
        submission_id: Broker submission reference
        named_insured: Full legal name of the first named insured
        fein: Federal employer identification number
        additional_named_insureds: Affiliated entities
        dba_names: Trading names
        first_location_address: Street address of the first location
        first_location_postal_code: Postal code of the first location
        broker_agency_name: Producing broker
        requested_effective_date: Requested effective date
        policy_register: In-force policies to clear against
        open_submissions: Open submissions to clear against

    Returns:
        Clearance status, matched records, controlling broker and routing
    """

    # ---------------------------------------------------------------------------
    # TODO — YOUR IMPLEMENTATION GOES HERE
    #
    # Specification below. The verification harness is the acceptance test:
    #     python3 training/scripts/verify_training_setup.py --from-actions-dir
    #
    # Do not change the function signature or the @apex_action schema above — the
    # harness calls this signature, and the schema is the contract other actions
    # and the playbook recipe rely on.
    # ---------------------------------------------------------------------------

    # Build the full identity set with _build_identity_set() — an account arrives
    #   under its own name, its affiliates' names and its trading names.
    # Compare against BOTH the policy register and the open-submission pipeline
    #   using _compare(). Never clear a submission against itself.
    # Classify, and mind the precedence — a renewal outranks a broker conflict,
    #   because a renewal is ours regardless of who brought it:
    #     in-force policy match          -> renewal, queue cp-renewals
    #     open submission, SAME broker   -> same_broker_resubmission (merge)
    #     open submission, OTHER broker  -> broker_conflict, queue cp-bor-conflict
    #     nothing                        -> clear, queue cp-new-business
    # blocking_conflict is True for everything except 'clear'.
    # clearance_note is read by a human — say which record matched, on what basis,
    #   at what confidence, and what they should do about it.

    raise NotImplementedError("submission_clear: see the TODO above")


# ============================================================================
# Matching
# ============================================================================

def _compare(
    record: Dict[str, Any],
    identities: set,
    norm_fein: str,
    norm_address: str,
    postal_code: Optional[str],
    record_type: str,
) -> Optional[Dict[str, Any]]:
    """Compare one register or pipeline record. Returns a match or None."""

    # ---------------------------------------------------------------------------
    # TODO — YOUR IMPLEMENTATION GOES HERE
    #
    # Specification below. The verification harness is the acceptance test:
    #     python3 training/scripts/verify_training_setup.py --from-actions-dir
    #
    # Do not change the function signature or the @apex_action schema above — the
    # harness calls this signature, and the schema is the contract other actions
    # and the playbook recipe rely on.
    # ---------------------------------------------------------------------------

    # Compare one register/pipeline record against this submission. Return a
    # _match() or None.
    #   FEIN      conclusive. Equal normalised FEINs -> confidence 1.00, done.
    #   name      best score across every identity on BOTH sides. At or above
    #             NAME_MATCH_FLOOR it is a match; if the first-location address
    #             ALSO matches, raise confidence (cap at 0.99).
    #   address   only when the name did not match: identical normalised address
    #             AND identical 5-digit postal code, at 0.90 weight. This catches
    #             a renamed entity — report it as such.
    # Everything else is None.

    raise NotImplementedError("_compare: see the TODO above")


def _match(
    record: Dict[str, Any],
    record_type: str,
    basis: str,
    confidence: float,
    detail: str,
) -> Dict[str, Any]:
    return {
        "record_type": record_type,
        "record_id": (
            record.get("policy_number")
            or record.get("submission_id")
            or record.get("record_id")
        ),
        "named_insured": record.get("named_insured") or record.get("insured_name"),
        "fein": record.get("fein"),
        "broker_agency_name": record.get("broker_agency_name"),
        "effective_date": record.get("effective_date"),
        "expiration_date": record.get("expiration_date"),
        "received_date": record.get("received_date"),
        "status": record.get("status"),
        "match_basis": basis,
        "confidence": round(confidence, 4),
        "match_detail": detail,
    }


# ============================================================================
# Normalisation helpers
# ============================================================================

def _build_identity_set(
    primary: str,
    additional: Optional[List[str]],
    dbas: Optional[List[str]],
) -> set:
    """Every normalised name this account could be known by."""
    names = [primary or ""]
    names.extend(additional or [])
    names.extend(dbas or [])
    return {n for n in (_normalise_entity(x) for x in names) if n}


def _normalise_entity(value: str) -> str:
    """Upper-case, strip punctuation and drop corporate suffixes."""
    if not value:
        return ""
    s = str(value).upper()
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    for suffix in _ENTITY_SUFFIXES:
        s = re.sub(rf"\b{suffix}\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _normalise_fein(value: Any) -> str:
    """Digits only, so 47-3319008 and 473319008 compare equal."""
    if not value:
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits if len(digits) == 9 else ""


def _normalise_address(value: Optional[str]) -> str:
    """
    Normalise street type abbreviations and directionals so
    "1420 N. Industrial Blvd." and "1420 North Industrial Boulevard" match.
    """
    if not value:
        return ""
    s = str(value).upper()
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    replacements = {
        r"\bSTREET\b": "ST", r"\bAVENUE\b": "AVE", r"\bBOULEVARD\b": "BLVD",
        r"\bDRIVE\b": "DR", r"\bROAD\b": "RD", r"\bLANE\b": "LN",
        r"\bPARKWAY\b": "PKWY", r"\bHIGHWAY\b": "HWY", r"\bCOURT\b": "CT",
        r"\bSUITE\b": "STE", r"\bBUILDING\b": "BLDG",
        r"\bNORTH\b": "N", r"\bSOUTH\b": "S", r"\bEAST\b": "E", r"\bWEST\b": "W",
        r"\bNORTHEAST\b": "NE", r"\bNORTHWEST\b": "NW",
        r"\bSOUTHEAST\b": "SE", r"\bSOUTHWEST\b": "SW",
    }
    for pattern, short in replacements.items():
        s = re.sub(pattern, short, s)
    return re.sub(r"\s+", " ", s).strip()


def _ratio(a: str, b: str) -> float:
    """Character-bigram Dice coefficient. Dependency-free for bare Lambda."""
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) < 2 or len(b) < 2:
        return 1.0 if a == b else 0.0
    bg_a = {a[i:i + 2] for i in range(len(a) - 1)}
    bg_b = {b[i:i + 2] for i in range(len(b) - 1)}
    if not bg_a or not bg_b:
        return 0.0
    return (2.0 * len(bg_a & bg_b)) / (len(bg_a) + len(bg_b))


def _table(table_name: str):
    """
    Return a boto3-style table handle on EITHER cloud.

    The Azure build ships `sdk/azure_data.py`, a shim exposing the same surface
    as `boto3.resource("dynamodb")`. Import it first and fall back to boto3, and
    the handler body is identical on AWS and Azure. With USE_LOCAL_MOCK=true the
    Azure shim reads an on-disk store, so this also runs with no cloud account.
    """
    try:
        from sdk.azure_data import get_table_resource       # Azure build
        return get_table_resource().Table(table_name)
    except ImportError:
        import boto3                                         # AWS build
        return boto3.resource("dynamodb").Table(table_name)


def _load_table(env_var: str, default_table: str) -> List[Dict[str, Any]]:
    """
    Read a clearance table from the table store when the caller did not supply rows.

    Returns an empty list on failure. The playbook recipe requires the agent to
    treat an unreachable register as a manual-clearance referral rather than as
    "clear" — failing open on clearance causes broker conflicts.
    """
    try:
        table_name = os.environ.get(env_var, default_table)
        return _table(table_name).scan(Limit=1000).get("Items", [])
    except Exception:
        return []


def _f(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


# ============================================================================
# Class-based implementation
# ============================================================================

class SubmissionClearAction(ApexActionBase):
    """Submission Clearance Action (class-based)."""

    name = "submission_clear"
    description = "Clear a submission against in-force policies and open submissions"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return submission_clear(**kwargs)


def handler(event, context):
    """Lambda entry point."""
    return submission_clear(**event)
