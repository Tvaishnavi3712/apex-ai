"""
Azure ML adapter — the Azure implementation of Apex Signal's predictor.

Replaces Azure ML managed endpoints with **Azure ML managed online endpoints**.

Design
------
`AzureMLPredictor` keeps ALL of its business logic — feature shaping, response
parsing, and the deterministic fallbacks that keep Apex Signal working when an
endpoint is unavailable. Only three things actually touch the cloud:

    _invoke_csv()   _invoke_json()   endpoint_status()

so this class subclasses the original and overrides just those. Every
`predict_*` / `forecast_*` / `detect_*` method therefore works unchanged, and
the fallback behaviour is preserved exactly.

Azure ML online endpoints are scored over HTTPS:
    POST https://<endpoint>.<region>.inference.ml.azure.com/score
with an Entra ID bearer token (no keys).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import structlog

from services.prediction_base import PredictionBase

log = structlog.get_logger()


class AzureMLPredictor(PredictionBase):
    """Azure ML implementation of the Apex predictor port."""

    def __init__(self, region: str = "eastus") -> None:
        # Deliberately skip PredictionBase.__init__ (it builds boto3 clients).
        self.region = os.environ.get("AZURE_LOCATION", region)
        self.workspace = os.environ.get("AZURE_ML_WORKSPACE", "")
        self.base_domain = os.environ.get(
            "AZURE_ML_ENDPOINT_DOMAIN", f"{self.region}.inference.ml.azure.com"
        )
        self._use_mock = os.environ.get("USE_LOCAL_MOCK", "false").lower() == "true"
        self._token = None
        self._client = None  # unused on Azure; kept so inherited code never breaks

    # ── auth ─────────────────────────────────────────────────────────────────
    def _bearer(self) -> str:
        """Entra ID token for Azure ML scoring (cached per process)."""
        if self._token:
            return self._token
        from azure.identity import DefaultAzureCredential

        cred = DefaultAzureCredential()
        self._token = cred.get_token("https://ml.azure.com/.default").token
        return self._token

    def _scoring_uri(self, endpoint: str) -> str:
        """Explicit override wins, else the conventional Azure ML URL."""
        override = os.environ.get(f"AZURE_ML_URI_{endpoint.upper().replace('-', '_')}")
        return override or f"https://{endpoint}.{self.base_domain}/score"

    def _post(self, endpoint: str, body: Any, content_type: str) -> Any:
        import httpx

        resp = httpx.post(
            self._scoring_uri(endpoint),
            content=body if isinstance(body, (bytes, str)) else json.dumps(body),
            headers={
                "Content-Type": content_type,
                "Authorization": f"Bearer {self._bearer()}",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp

    # ── overrides: the only AWS-touching methods ─────────────────────────────
    def _invoke_csv(
        self,
        endpoint: str,
        payload: str,
        default: Any,
        content_type: str = "text/csv",
        accept: str = "text/csv",
    ) -> Any:
        """CSV-style scoring. Falls back to `default` exactly like the AWS path."""
        if self._use_mock:
            return default
        try:
            body = self._post(endpoint, payload, content_type).text.strip()
            if accept == "application/json":
                return json.loads(body)
            if "," in body:
                return [float(x) for x in body.split(",")]
            return float(body)
        except Exception as e:  # noqa: BLE001
            log.warning("azure_ml.invoke_failed", endpoint=endpoint, error=str(e))
            return default

    def _invoke_json(
        self, endpoint: str, payload: Dict[str, Any], default: Dict[str, Any]
    ) -> Dict[str, Any]:
        """JSON scoring. Falls back to `default` exactly like the AWS path."""
        if self._use_mock:
            return default
        try:
            return self._post(endpoint, payload, "application/json").json()
        except Exception as e:  # noqa: BLE001
            log.warning("azure_ml.invoke_failed", endpoint=endpoint, error=str(e))
            return default

    # ── health ───────────────────────────────────────────────────────────────
    def _status_for(self, names: List[str]) -> Dict[str, str]:
        if self._use_mock or not self.workspace:
            return {n: "NotDeployed" for n in names}

        result: Dict[str, str] = {}
        try:
            from azure.ai.ml import MLClient
            from azure.identity import DefaultAzureCredential

            ml = MLClient(
                DefaultAzureCredential(),
                os.environ.get("AZURE_SUBSCRIPTION_ID", ""),
                os.environ.get("AZURE_RESOURCE_GROUP", ""),
                self.workspace,
            )
            live = {e.name for e in ml.online_endpoints.list()}
            for n in names:
                result[n] = "InService" if n in live else "NotDeployed"
        except Exception as e:  # noqa: BLE001
            log.warning("azure_ml.status_failed", error=str(e))
            result = {n: "Unknown" for n in names}
        return result

    def endpoint_status(self) -> Dict[str, str]:
        from core.config import settings

        return self._status_for([
            settings.AZUREML_ENDPOINT_LEAD_TIME,
            settings.AZUREML_ENDPOINT_SUPPLIER,
            settings.AZUREML_ENDPOINT_STOCKOUT,
            settings.AZUREML_ENDPOINT_DEMAND,
        ])

    def eprod_endpoint_status(self) -> Dict[str, str]:
        from core.config import settings

        names = [
            getattr(settings, n)
            for n in dir(settings)
            if n.startswith("AZUREML_ENDPOINT_EPROD")
        ]
        return self._status_for(names or [])


# Provider-neutral alias.
Predictor = AzureMLPredictor
