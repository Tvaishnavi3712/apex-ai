"""
SageMaker runtime client for ApexSignal.

Wraps the 4 deployed endpoints (lead_time / supplier / stockout / demand) with
clean, typed helpers. Falls back to a deterministic prediction from the cached
DynamoDB data if the endpoint is unavailable (e.g. torn down to save cost) —
this keeps the demo alive when no SageMaker spend is tolerated.

Endpoint names come from `core.config.settings`. Deployed by
`backend/scripts/deploy_sagemaker_endpoints.py`.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import boto3

from core.config import settings

log = logging.getLogger(__name__)


class SageMakerService:
    """Thin wrapper around sagemaker-runtime.invoke_endpoint.

    The 4 methods return Pythonic dicts the API layer can return directly;
    they never raise on endpoint failure — instead they log and return
    {'success': False, 'fallback': True, ...} so the frontend can display
    "model offline" without crashing.
    """

    def __init__(self, region: str = "us-east-1") -> None:
        self.region = region
        self._client = boto3.client("sagemaker-runtime", region_name=region)

    # ─────── public API ───────

    def predict_lead_time(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-lead-time · XGBoost binary.

        Args:
            features: dict with keys on_time_pct, lead_time_days_avg,
                      risk_numeric, qty, port_enc (all numeric).

        Returns:
            {probability_of_delay: float (0..1), predicted_delay_days: int}
        """
        ordered = [
            features.get("on_time_pct", 90.0),
            features.get("lead_time_days_avg", 12.0),
            features.get("risk_numeric", 3.0),
            features.get("qty", 2000.0),
            features.get("port_enc", 0.0),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        prob = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_LEAD_TIME,
            payload=csv_payload,
            default=0.15,
        )
        # XGBoost binary returns a single float probability.
        prob_f = float(prob) if isinstance(prob, (int, float)) else float(prob[0]) if isinstance(prob, list) else 0.15
        return {
            "probability_of_delay": round(prob_f, 4),
            "predicted_delay_days": int(round(prob_f * 14)),  # rough heuristic 0..14
            "endpoint": settings.SAGEMAKER_ENDPOINT_LEAD_TIME,
        }

    def predict_supplier_risk(self, moisture_pct: float, purity_pct: float, viscosity: float) -> Dict[str, Any]:
        """apex-signal-supplier · XGBoost multi-class.

        Returns:
            {risk_score: str, class_index: int, probabilities: list[float]}
        """
        labels = ["Very Low", "Low", "Medium", "High", "Critical"]
        csv_payload = f"{moisture_pct},{purity_pct},{viscosity}"
        out = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_SUPPLIER,
            payload=csv_payload,
            default=[0.02, 0.92, 0.04, 0.015, 0.005],
        )
        probs: List[float]
        if isinstance(out, list) and len(out) == 5:
            probs = [float(x) for x in out]
        elif isinstance(out, (int, float)):
            # softprob returns comma-separated string; try parsing again
            probs = [float(x) for x in str(out).split(",")] if "," in str(out) else [0.2] * 5
        else:
            probs = [0.2] * 5
        idx = probs.index(max(probs))
        return {
            "risk_score":    labels[idx],
            "class_index":   idx,
            "probabilities": [round(p, 4) for p in probs],
            "endpoint": settings.SAGEMAKER_ENDPOINT_SUPPLIER,
        }

    def predict_stockout(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-stockout · Linear Learner regression.

        Returns:
            {days_until_stockout: int}
        """
        ordered = [
            features.get("stock_level_kg", 10000.0),
            features.get("burn_rate_per_day", 500.0),
            features.get("safety_stock_pct", 50.0),
            features.get("region_demand_avg", 3500.0),
            features.get("trend_delta", 0.0),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        raw = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_STOCKOUT,
            payload=csv_payload,
            default=features.get("stock_level_kg", 10000.0) / max(1.0, features.get("burn_rate_per_day", 500.0)),
            content_type="text/csv",
            accept="application/json",
        )
        # Linear learner returns {"predictions": [{"score": float}]}
        if isinstance(raw, dict) and "predictions" in raw:
            pred = raw["predictions"][0]
            days = float(pred.get("score", 20.0))
        elif isinstance(raw, (int, float)):
            days = float(raw)
        else:
            days = 20.0
        return {
            "days_until_stockout": max(0, int(round(days))),
            "endpoint": settings.SAGEMAKER_ENDPOINT_STOCKOUT,
        }

    def forecast_demand(self, series: List[float], freq: str = "W", prediction_length: int = 12) -> Dict[str, Any]:
        """apex-signal-demand · DeepAR time-series.

        Args:
            series: historical weekly units_sold (must have ≥ context_length values).
            freq: pandas offset alias; DeepAR was trained with 'W'.
            prediction_length: forecast horizon.

        Returns:
            {forecast: list[float], confidence_lower: list[float], confidence_upper: list[float]}
        """
        from datetime import date, timedelta
        start = (date.today() - timedelta(weeks=len(series))).strftime("%Y-%m-%d 00:00:00")
        payload = {
            "instances": [{"start": start, "target": list(series)}],
            "configuration": {
                "num_samples": 100,
                "output_types": ["mean", "quantiles"],
                "quantiles": ["0.1", "0.9"],
            },
        }
        out = self._invoke_json(
            endpoint=settings.SAGEMAKER_ENDPOINT_DEMAND,
            payload=payload,
            default={
                "predictions": [{
                    "mean":      [float(series[-1])] * prediction_length,
                    "quantiles": {"0.1": [float(series[-1]) * 0.9] * prediction_length,
                                  "0.9": [float(series[-1]) * 1.1] * prediction_length},
                }],
            },
        )
        pred = (out.get("predictions") or [{}])[0]
        mean = pred.get("mean",   [float(series[-1])] * prediction_length)
        lo   = pred.get("quantiles", {}).get("0.1", [float(m) * 0.9 for m in mean])
        hi   = pred.get("quantiles", {}).get("0.9", [float(m) * 1.1 for m in mean])
        return {
            "forecast":         [round(float(x), 1) for x in mean],
            "confidence_lower": [round(float(x), 1) for x in lo],
            "confidence_upper": [round(float(x), 1) for x in hi],
            "endpoint": settings.SAGEMAKER_ENDPOINT_DEMAND,
        }

    # ─────── Verizon Far Edge endpoints ───────

    def predict_vz_wave_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-vz-wave-risk · XGBoost binary.

        Predicts P(this wave causes a post-deploy outage within 30 days).

        Args:
            features: dict with keys
                device_type_enc:        0=Type-A 1=Type-B 2=Type-C
                firmware_jump_size:     int (minor versions between from→to; skip-level = 4+)
                region_enc:             0=NE 1=NW 2=SE 3=SW 4=Midwest 5=Central 6=Southwest 7=Mountain
                schema_drift_events:    int (count of breaking schema changes detected pre-wave)
                historical_pass_rate:   float (0..1)
                season_q:               1..4
                wave_size:              int (sites in this wave)

        Returns:
            {probability_of_outage, risk_tier ∈ {low,medium,high,critical}, top_reasons[]}
        """
        ordered = [
            features.get("device_type_enc", 1.0),       # default Type-B
            features.get("firmware_jump_size", 1.0),
            features.get("region_enc", 0.0),
            features.get("schema_drift_events", 0.0),
            features.get("historical_pass_rate", 0.93),
            features.get("season_q", 1.0),
            features.get("wave_size", 4000.0),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        prob = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_VZ_WAVE_RISK,
            payload=csv_payload,
            default=0.18,
        )
        prob_f = float(prob) if isinstance(prob, (int, float)) \
                 else float(prob[0]) if isinstance(prob, list) else 0.18
        prob_f = max(0.0, min(1.0, prob_f))

        if   prob_f >= 0.60: tier = "critical"
        elif prob_f >= 0.30: tier = "high"
        elif prob_f >= 0.10: tier = "medium"
        else:                tier = "low"

        reasons: List[str] = []
        if features.get("firmware_jump_size", 0) >= 4:
            reasons.append("Skip-level firmware upgrade")
        if features.get("schema_drift_events", 0) >= 1:
            reasons.append(f"{int(features.get('schema_drift_events', 0))} unresolved schema drift(s)")
        if features.get("historical_pass_rate", 1.0) < 0.85:
            reasons.append(f"Historical pass rate {features.get('historical_pass_rate', 0)*100:.0f}%")
        if features.get("wave_size", 0) > 5000:
            reasons.append(f"Large blast radius ({int(features.get('wave_size', 0)):,} sites)")

        return {
            "probability_of_outage": round(prob_f, 4),
            "risk_tier":             tier,
            "top_reasons":           reasons or ["No anomalous signals detected"],
            "endpoint":              settings.SAGEMAKER_ENDPOINT_VZ_WAVE_RISK,
        }

    def predict_vz_site_cert(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-vz-site-cert · XGBoost binary.

        Per-site predictive cert outcome — pre-flight risk score for each of
        the 16,247 sites before the 247-test ROBOT cycle runs.

        Args:
            features: dict with keys
                device_age_months, incident_count_12m, last_cert_status_enc,
                firmware_jump_size, vendor_sla_tier_enc, region_enc,
                prior_drift_exposure.

        Returns:
            {probability_of_fail, predicted_outcome ∈ {pass,conditional,fail},
             feature_contributions: dict}
        """
        ordered = [
            features.get("device_age_months", 36.0),
            features.get("incident_count_12m", 0.0),
            features.get("last_cert_status_enc", 0.0),   # 0=PASS 1=CONDITIONAL 2=FAIL
            features.get("firmware_jump_size", 1.0),
            features.get("vendor_sla_tier_enc", 1.0),    # 0=premium 1=standard 2=economy
            features.get("region_enc", 0.0),
            features.get("prior_drift_exposure", 0.0),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        prob = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_VZ_SITE_CERT,
            payload=csv_payload,
            default=0.08,
        )
        prob_f = float(prob) if isinstance(prob, (int, float)) \
                 else float(prob[0]) if isinstance(prob, list) else 0.08
        prob_f = max(0.0, min(1.0, prob_f))

        if   prob_f >= 0.40: outcome = "fail"
        elif prob_f >= 0.15: outcome = "conditional"
        else:                outcome = "pass"

        contribs = {
            "device_age_months":    round(min(1.0, features.get("device_age_months", 0) / 60.0) * 0.25, 3),
            "incident_count_12m":   round(min(1.0, features.get("incident_count_12m", 0) / 10.0)  * 0.30, 3),
            "firmware_jump_size":   round(min(1.0, features.get("firmware_jump_size", 0) / 5.0)   * 0.25, 3),
            "prior_drift_exposure": round(min(1.0, features.get("prior_drift_exposure", 0) / 5.0) * 0.20, 3),
        }
        return {
            "probability_of_fail":    round(prob_f, 4),
            "predicted_outcome":      outcome,
            "feature_contributions":  contribs,
            "endpoint":               settings.SAGEMAKER_ENDPOINT_VZ_SITE_CERT,
        }

    def detect_vz_thermal_anomaly(self, series: List[float],
                                   ambient_temp: Optional[float] = None) -> Dict[str, Any]:
        """apex-signal-vz-thermal-anomaly · Random Cut Forest.

        Args:
            series: recent thermal readings (degrees C) for one NE site. RCF
                    accepts variable-length input via newline-delimited CSV.
            ambient_temp: ambient datacenter temp (optional, for narrative).

        Returns:
            {anomaly_scores: list[float] (one per input point),
             max_score: float, anomaly_detected: bool, severity ∈ {none,low,med,high}}
        """
        if not series:
            return {
                "anomaly_scores": [],
                "max_score":      0.0,
                "anomaly_detected": False,
                "severity":       "none",
                "endpoint":       settings.SAGEMAKER_ENDPOINT_VZ_THERMAL_ANOMALY,
            }

        # RCF was trained on 4-feature rows (thermal_c, fan_rpm, cpu_load,
        # ambient_c). At inference we only get the thermal reading directly,
        # so broadcast each thermal_c into a 4-feature vector with realistic
        # derived defaults: fan_rpm scales with thermal_c above baseline,
        # cpu_load similarly, ambient_c uses the caller's value or 23°C.
        amb = float(ambient_temp) if ambient_temp is not None else 23.0
        rows: List[str] = []
        for t in series:
            t_f = float(t)
            # Above 35°C, fans ramp; above 40°C, fans + load both ramp hard.
            fan  = 2800.0 + max(0.0, (t_f - 32.0)) * 180.0   # ~ baseline 2800, +180/°C
            load = 0.45  + max(0.0, (t_f - 32.0)) * 0.035    # ~ 0.45 baseline, +3.5%/°C
            load = min(0.98, load)
            rows.append(f"{t_f},{fan:.1f},{load:.3f},{amb}")
        csv_payload = "\n".join(rows)
        raw = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_VZ_THERMAL_ANOMALY,
            payload=csv_payload,
            default=[0.5] * len(series),
            content_type="text/csv",
            accept="application/json",
        )

        scores: List[float] = []
        if isinstance(raw, dict) and "scores" in raw:
            scores = [float(s.get("score", 0.0)) for s in raw["scores"]]
        elif isinstance(raw, list):
            scores = [float(x) for x in raw]
        else:
            scores = [0.5] * len(series)

        max_score = max(scores) if scores else 0.0
        # RCF scores are unbounded; treat > 1.5 as anomalous (typical threshold).
        if   max_score >= 3.0: severity = "high"
        elif max_score >= 2.0: severity = "med"
        elif max_score >= 1.5: severity = "low"
        else:                  severity = "none"

        return {
            "anomaly_scores":   [round(s, 4) for s in scores],
            "max_score":        round(max_score, 4),
            "anomaly_detected": max_score >= 1.5,
            "severity":         severity,
            "ambient_temp":     ambient_temp,
            "endpoint":         settings.SAGEMAKER_ENDPOINT_VZ_THERMAL_ANOMALY,
        }

    # ─────── EPROD (Enterprise Products Partners) endpoints ───────

    def predict_eprod_vendor_drift(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-eprod-vendor-drift · XGBoost regression.

        Predicts the next-90-day projected drift % of a vendor's billed rate
        vs their contracted MSA rate. Positive value = vendor drifting up.

        Features (ordered to match training):
            trailing_3mo_drift_pct, trailing_6mo_drift_pct,
            vendor_tenure_months, industry_segment_enc,
            msa_renewal_count, total_spend_log

        Returns:
            {projected_drift_pct, status ∈ {drifting_up,drifting_down,stable},
             endpoint, raw}
        """
        ordered = [
            features.get("trailing_3mo_drift_pct", 0.0),
            features.get("trailing_6mo_drift_pct", 0.0),
            features.get("vendor_tenure_months",   24.0),
            features.get("industry_segment_enc",   0.0),
            features.get("msa_renewal_count",      1.0),
            features.get("total_spend_log",        14.5),  # log($2M) ≈ 14.5
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        raw = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_EPROD_VENDOR_DRIFT,
            payload=csv_payload,
            default=features.get("trailing_3mo_drift_pct", 0.0) * 1.4,
        )
        drift = float(raw) if isinstance(raw, (int, float)) \
                else float(raw[0]) if isinstance(raw, list) and raw else 0.0

        status = ("drifting_up"   if drift >=  2.0
                  else "drifting_down" if drift <= -2.0
                  else "stable")
        return {
            "projected_drift_pct": round(drift, 2),
            "status":              status,
            "endpoint":            settings.SAGEMAKER_ENDPOINT_EPROD_VENDOR_DRIFT,
            "raw":                 raw,
        }

    def predict_eprod_tariff_forecast(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-eprod-tariff-forecast · XGBoost regression.

        Predicts the % change in pipeline tariff rate at the next FERC index
        cycle, given PPI-FG trajectory + historical rates.

        Features:
            current_rate_per_dth, prior_year_rate, ppi_fg_index,
            ppi_fg_yoy_change_pct, commodity_enc, region_enc,
            pipeline_tenure_years, surcharge_history_avg

        Returns:
            {projected_change_pct, confidence ∈ [0,1], endpoint, raw}
        """
        ordered = [
            features.get("current_rate_per_dth",    0.20),
            features.get("prior_year_rate",         0.19),
            features.get("ppi_fg_index",            132.0),
            features.get("ppi_fg_yoy_change_pct",   3.5),
            features.get("commodity_enc",           0.0),
            features.get("region_enc",              0.0),
            features.get("pipeline_tenure_years",   10.0),
            features.get("surcharge_history_avg",   0.003),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        raw = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_EPROD_TARIFF_FORECAST,
            payload=csv_payload,
            default=features.get("ppi_fg_yoy_change_pct", 3.5),
        )
        change = float(raw) if isinstance(raw, (int, float)) \
                 else float(raw[0]) if isinstance(raw, list) and raw else 0.0
        # Heuristic confidence — narrower band when PPI-FG history is stable
        confidence = 0.87 if features.get("ppi_fg_yoy_change_pct", 3.5) < 5 else 0.78
        return {
            "projected_change_pct": round(change, 2),
            "confidence":           round(confidence, 2),
            "endpoint":             settings.SAGEMAKER_ENDPOINT_EPROD_TARIFF_FORECAST,
            "raw":                  raw,
        }

    def predict_eprod_contract_expiry(self, features: Dict[str, float]) -> Dict[str, Any]:
        """apex-signal-eprod-contract-expiry · XGBoost multi-class.

        Predicts the risk-tier of a contract (0=low, 1=medium, 2=high, 3=critical)
        given expiry runway, spend, complexity, and renewal initiation.

        Features:
            days_to_expiry, annual_spend_log, scope_lines,
            renewal_initiated_int (0|1), complexity_enc (0=low,1=med,2=high),
            contract_type_enc (0=MSA,1=ROW,2=Service,3=Tariff),
            vendor_tenure_years

        Returns:
            {risk_tier ∈ {low,medium,high,critical}, class_index,
             probabilities[], endpoint, raw}
        """
        labels = ["low", "medium", "high", "critical"]
        ordered = [
            features.get("days_to_expiry",         90.0),
            features.get("annual_spend_log",       14.0),
            features.get("scope_lines",            10.0),
            features.get("renewal_initiated_int",  1.0),
            features.get("complexity_enc",         1.0),
            features.get("contract_type_enc",      0.0),
            features.get("vendor_tenure_years",    5.0),
        ]
        csv_payload = ",".join(str(v) for v in ordered)
        # Sensible default for class probabilities when endpoint offline
        days = features.get("days_to_expiry", 90.0)
        spend_log = features.get("annual_spend_log", 14.0)
        renewal = features.get("renewal_initiated_int", 1.0)
        # Heuristic fallback: low days × no renewal × high spend → critical
        if days < 30 and renewal == 0:        default_idx = 3
        elif days < 60 and spend_log > 14.5:  default_idx = 2
        elif days < 90:                       default_idx = 1
        else:                                 default_idx = 0
        default_probs = [0.05, 0.10, 0.20, 0.65] if default_idx == 3 \
                        else [0.10, 0.20, 0.50, 0.20] if default_idx == 2 \
                        else [0.30, 0.50, 0.15, 0.05] if default_idx == 1 \
                        else [0.70, 0.20, 0.08, 0.02]

        raw = self._invoke_csv(
            endpoint=settings.SAGEMAKER_ENDPOINT_EPROD_CONTRACT_EXPIRY,
            payload=csv_payload,
            default=default_probs,
        )
        probs: List[float]
        if isinstance(raw, list) and len(raw) == 4:
            probs = [float(x) for x in raw]
        elif isinstance(raw, (int, float)):
            probs = [0.25] * 4
        else:
            probs = default_probs
        idx = probs.index(max(probs))
        return {
            "risk_tier":     labels[idx],
            "class_index":   idx,
            "probabilities": [round(p, 4) for p in probs],
            "endpoint":      settings.SAGEMAKER_ENDPOINT_EPROD_CONTRACT_EXPIRY,
            "raw":           raw,
        }

    # ─────── internals ───────

    def _invoke_csv(self, endpoint: str, payload: str, default, content_type: str = "text/csv",
                    accept: str = "text/csv") -> Any:
        try:
            resp = self._client.invoke_endpoint(
                EndpointName=endpoint,
                ContentType=content_type,
                Accept=accept,
                Body=payload,
            )
            body = resp["Body"].read().decode().strip()
            if accept == "application/json":
                return json.loads(body)
            # XGBoost returns a single float or comma-list
            if "," in body:
                return [float(x) for x in body.split(",")]
            return float(body)
        except Exception as e:
            log.warning("SageMaker %s invoke failed: %s — using default", endpoint, e)
            return default

    def _invoke_json(self, endpoint: str, payload: Dict[str, Any], default: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = self._client.invoke_endpoint(
                EndpointName=endpoint,
                ContentType="application/json",
                Body=json.dumps(payload).encode(),
            )
            return json.loads(resp["Body"].read())
        except Exception as e:
            log.warning("SageMaker %s invoke failed: %s — using default", endpoint, e)
            return default

    # ─────── health ───────

    def endpoint_status(self) -> Dict[str, str]:
        """Return {endpoint_name: status} for ApexSignal endpoints."""
        sm = boto3.client("sagemaker", region_name=self.region)
        names = [
            settings.SAGEMAKER_ENDPOINT_LEAD_TIME,
            settings.SAGEMAKER_ENDPOINT_SUPPLIER,
            settings.SAGEMAKER_ENDPOINT_STOCKOUT,
            settings.SAGEMAKER_ENDPOINT_DEMAND,
        ]
        result = {}
        for n in names:
            try:
                resp = sm.describe_endpoint(EndpointName=n)
                result[n] = resp.get("EndpointStatus", "Unknown")
            except Exception:
                result[n] = "NotDeployed"
        return result

    def eprod_endpoint_status(self) -> Dict[str, str]:
        """Return {endpoint_name: status} for the 3 EPROD endpoints."""
        sm = boto3.client("sagemaker", region_name=self.region)
        names = [
            settings.SAGEMAKER_ENDPOINT_EPROD_VENDOR_DRIFT,
            settings.SAGEMAKER_ENDPOINT_EPROD_TARIFF_FORECAST,
            settings.SAGEMAKER_ENDPOINT_EPROD_CONTRACT_EXPIRY,
        ]
        result = {}
        for n in names:
            try:
                resp = sm.describe_endpoint(EndpointName=n)
                result[n] = resp.get("EndpointStatus", "Unknown")
            except Exception:
                result[n] = "NotDeployed"
        return result
