"""
compute_risk_scores — ApexSignal predictive risk scoring for the Verizon Far
Edge wave deployment. Reads the site inventory CSV and historical failure
patterns CSV, computes a 0.0-1.0 risk score per site with deterministic
override rules (e.g. the high-risk Type-B Northeast deployment pattern), and
returns wave-sequencing recommendations.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.telecommunications._shared import load_csv, missing_data_envelope  # noqa: E402


def _firmware_age_score(fw: str) -> float:
    return {"22.06": 0.95, "22.12": 0.85, "23.06": 0.75, "23.12": 0.55,
            "24.01": 0.35, "24.06": 0.20, "24.12": 0.10}.get(fw, 0.50)


def _classify_tier(score: float) -> str:
    if score > 0.65:
        return "critical"
    if score > 0.40:
        return "high"
    if score > 0.20:
        return "medium"
    return "low"


def _historical_failure_rate(device: str, fw_from: str, fw_to: str, region: str,
                             patterns: List[Dict[str, str]]) -> Optional[float]:
    """Average post_upgrade_incidents_30d > 0 rate for matching rows."""
    matches = [p for p in patterns
               if p.get("device_type") == device
               and p.get("firmware_from") == fw_from
               and p.get("firmware_to") == fw_to
               and p.get("region") == region]
    if not matches:
        return None
    fails = sum(1 for m in matches if m.get("outage_occurred", "").lower() == "true"
                                   or int(m.get("post_upgrade_incidents_30d", 0)) > 5)
    return round(fails / len(matches), 3)


@apex_action(ApexActionSchema(
    name="compute_risk_scores",
    description="ApexSignal — score every site in the inventory and produce wave assignments.",
    category="ml_inference",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="Risk scoring request")
        .add_string("inventory_path",         "Path to site inventory CSV. Defaults to bundled wave1 CSV.", required=False)
        .add_string("historical_patterns_path","Path to historical patterns CSV. Defaults to bundled patterns.", required=False)
        .add_string("region_filter",          "Optional: only score sites in this region", required=False),
    output_schema=ActionOutputSchema(description="Risk scoring envelope")
        .add_string("status", "ok | error")
        .add_number("total_sites_scored",  "Total sites scored")
        .add_string("tier_counts",         "Tier counts {critical, high, medium, low}")
        .add_string("wave_counts",         "{wave_1, wave_2, wave_3}")
        .add_number("january_2026_pattern_matches", "Sites matching Type-B/23.06/Northeast")
        .add_string("critical_clusters",   "Critical-tier sites grouped by region")
        .add_string("top_10_highest_risk", "Top 10 highest-risk sites")
        .add_string("scored_sites",        "Per-site enriched records")
        .add_string("recommended_action",  "HOLD | PROCEED_WITH_HITL | PROCEED"),
))
def compute_risk_scores(
    inventory_path: Optional[str] = None,
    historical_patterns_path: Optional[str] = None,
    region_filter: Optional[str] = None,
) -> Dict[str, Any]:
    inv = load_csv(inventory_path or "inventory/verizon_site_inventory_wave1.csv")
    if not inv:
        return missing_data_envelope("inventory/verizon_site_inventory_wave1.csv")
    patterns = load_csv(historical_patterns_path or "inventory/historical_failure_patterns.csv")

    scored: List[Dict[str, Any]] = []
    jan_pattern = 0
    for s in inv:
        if region_filter and s.get("region") != region_filter:
            continue
        device   = s.get("device_type", "")
        fw_from  = s.get("current_firmware", "")
        fw_to    = s.get("target_firmware", "")
        region   = s.get("region", "")

        # Components
        incidents = int(s.get("incident_count_12m", 0) or 0)
        age_m     = int(s.get("device_age_months", 0) or 0)
        last_status = s.get("last_cert_status", "PASS")
        schema_v  = s.get("schema_version", "v1.14.0")

        hist_rate = _historical_failure_rate(device, fw_from, fw_to, region, patterns) or 0.0
        incident_score   = min(incidents / 5.0, 1.0)
        firmware_age     = _firmware_age_score(fw_from)
        device_age_score = min(age_m / 60.0, 1.0)
        schema_lag       = 0.3 if schema_v in ("v1.12.0", "v1.13.0") else 0.0
        cert_penalty     = 0.20 if last_status == "FAIL" else (0.08 if last_status == "CONDITIONAL_PASS" else 0.0)

        score = (
            hist_rate        * 0.40 +
            incident_score   * 0.25 +
            firmware_age     * 0.15 +
            device_age_score * 0.10 +
            schema_lag       * 0.10 +
            cert_penalty
        )

        # High-risk Type-B Northeast pattern override (skip-level 23.06→24.01)
        is_jan_pattern = (device == "CaaS-Node-Type-B" and fw_from == "23.06" and region == "Northeast")
        if is_jan_pattern:
            score = max(score, 0.92)
            jan_pattern += 1

        score = round(min(score, 1.0), 3)
        tier  = _classify_tier(score)
        wave  = "wave_3" if tier == "critical" else ("wave_2" if tier == "high" else "wave_1")

        top_factors = []
        if hist_rate >= 0.30:                top_factors.append({"factor": "historical_failure_rate", "value": hist_rate})
        if is_jan_pattern:                   top_factors.append({"factor": "january_2026_outage_pattern", "value": 0.92})
        if incidents >= 3:                   top_factors.append({"factor": "incident_count_12m", "value": incidents})
        if schema_lag > 0:                   top_factors.append({"factor": "schema_lag", "value": schema_v})

        scored.append({
            "site_id":            s.get("site_id"),
            "region":             region,
            "device_type":        device,
            "current_firmware":   fw_from,
            "target_firmware":    fw_to,
            "incident_count_12m": incidents,
            "last_cert_status":   last_status,
            "risk_score":         score,
            "risk_tier":          tier,
            "wave_assignment":    wave,
            "historical_failure_rate": hist_rate,
            "top_risk_factors":   top_factors[:3],
            "matches_january_2026_pattern": is_jan_pattern,
        })

    tier_counts = Counter(s["risk_tier"]      for s in scored)
    wave_counts = Counter(s["wave_assignment"] for s in scored)
    critical_clusters = defaultdict(list)
    for s in scored:
        if s["risk_tier"] == "critical":
            critical_clusters[s["region"]].append(s["site_id"])
    top_10 = sorted(scored, key=lambda s: -s["risk_score"])[:10]

    recommended_action = ("HOLD_FOR_HITL_APPROVAL"
                          if tier_counts.get("critical", 0) > 0 else "PROCEED")

    return {
        "status":                         "ok",
        "total_sites_scored":             len(scored),
        "tier_counts":                    dict(tier_counts),
        "wave_counts":                    dict(wave_counts),
        "january_2026_pattern_matches":   jan_pattern,
        "critical_clusters":              {k: v for k, v in critical_clusters.items()},
        "top_10_highest_risk":            top_10,
        "scored_sites":                   scored,
        "recommended_action":             recommended_action,
        "model_version":                  "apex-signal-verizon-wave-risk-v1",
    }
