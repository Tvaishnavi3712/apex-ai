#!/usr/bin/env python3
"""
Train + deploy the 3 EPROD SageMaker endpoints onto AWS us-east-1.

  apex-signal-eprod-vendor-drift     — XGBoost regression
  apex-signal-eprod-tariff-forecast  — XGBoost regression
  apex-signal-eprod-contract-expiry  — XGBoost multi-class classification

Training data is built by:
  synthetic-data/eprod/generate_ml_training_data.py
which writes CSVs to synthetic-data/eprod/ml_training/.

This script:
  1. Uploads each training CSV to s3://apex-ml-training-data-{ACCT}/eprod/
  2. Trains the model on SageMaker
  3. Deploys to a managed endpoint with the canonical name
  4. Prints the endpoint ARNs

Cost: 3 × ml.m5.large ≈ $7/day. Tear down with `--destroy`.

Run:
  cd backend && source venv/bin/activate
  python3 scripts/deploy_sagemaker_eprod_endpoints.py             # all 3
  python3 scripts/deploy_sagemaker_eprod_endpoints.py --only vendor_drift
  python3 scripts/deploy_sagemaker_eprod_endpoints.py --destroy

Prereqs:
  - synthetic-data/eprod/ml_training/*.csv exist
  - AWS creds have sagemaker:* + s3:* on the two buckets
  - The IAM role below exists (it already does, used by other scripts)
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
import sagemaker
from sagemaker import image_uris, Session
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput

REGION       = "us-east-1"
ACCOUNT_ID   = "457795063704"
ROLE_ARN     = f"arn:aws:iam::{ACCOUNT_ID}:role/service-role/AmazonSageMaker-ExecutionRole-20260114T081145"
TRAIN_BUCKET = f"apex-ml-training-data-{ACCOUNT_ID}"
MODEL_BUCKET = f"apex-ml-models-{ACCOUNT_ID}"
PREFIX       = "eprod"

INSTANCE_TYPE  = "ml.m5.large"
INSTANCE_COUNT = 1

ENDPOINTS = {
    "vendor_drift":     "apex-signal-eprod-vendor-drift",
    "tariff_forecast":  "apex-signal-eprod-tariff-forecast",
    "contract_expiry":  "apex-signal-eprod-contract-expiry",
}

REPO_ROOT      = Path(__file__).resolve().parents[2]
TRAIN_DATA_DIR = REPO_ROOT / "synthetic-data" / "eprod" / "ml_training"

s3   = boto3.client("s3", region_name=REGION)
sm   = boto3.client("sagemaker", region_name=REGION)
sess = Session(boto3.session.Session(region_name=REGION))


# ──────────────────────────── helpers ────────────────────────────

def _upload(local_path: Path, s3_key: str) -> str:
    if not local_path.exists():
        sys.exit(f"  ✗ missing training file: {local_path}\n"
                 f"    Run synthetic-data/eprod/generate_ml_training_data.py first.")
    s3.upload_file(str(local_path), TRAIN_BUCKET, s3_key)
    uri = f"s3://{TRAIN_BUCKET}/{s3_key}"
    print(f"    ↑ {local_path.name} → {uri}")
    return uri


def _ensure_bucket(bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        print(f"  · creating bucket s3://{bucket}")
        s3.create_bucket(Bucket=bucket)


# ───────────────────────── per-endpoint pipelines ─────────────────────────

def train_vendor_drift():
    print("\n── [1/3] apex-signal-eprod-vendor-drift · XGBoost regression ──")
    train_uri = _upload(TRAIN_DATA_DIR / "vendor_drift_train.csv",
                        f"{PREFIX}/vendor_drift/train.csv")
    val_uri   = _upload(TRAIN_DATA_DIR / "vendor_drift_validation.csv",
                        f"{PREFIX}/vendor_drift/validation.csv")

    img = image_uris.retrieve("xgboost", REGION, version="1.7-1")
    est = Estimator(
        image_uri=img,
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{MODEL_BUCKET}/eprod_vendor_drift/",
        sagemaker_session=sess,
    )
    est.set_hyperparameters(
        objective="reg:squarederror",
        num_round=100,
        eval_metric="rmse",
        max_depth=5,
        eta=0.1,
    )
    est.fit({
        "train":      TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri,   content_type="text/csv"),
    }, wait=True, logs=False)
    est.deploy(
        endpoint_name=ENDPOINTS["vendor_drift"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['vendor_drift']}")


def train_tariff_forecast():
    print("\n── [2/3] apex-signal-eprod-tariff-forecast · XGBoost regression ──")
    train_uri = _upload(TRAIN_DATA_DIR / "tariff_forecast_train.csv",
                        f"{PREFIX}/tariff_forecast/train.csv")
    val_uri   = _upload(TRAIN_DATA_DIR / "tariff_forecast_validation.csv",
                        f"{PREFIX}/tariff_forecast/validation.csv")

    img = image_uris.retrieve("xgboost", REGION, version="1.7-1")
    est = Estimator(
        image_uri=img,
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{MODEL_BUCKET}/eprod_tariff_forecast/",
        sagemaker_session=sess,
    )
    est.set_hyperparameters(
        objective="reg:squarederror",
        num_round=120,
        eval_metric="rmse",
        max_depth=5,
        eta=0.1,
    )
    est.fit({
        "train":      TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri,   content_type="text/csv"),
    }, wait=True, logs=False)
    est.deploy(
        endpoint_name=ENDPOINTS["tariff_forecast"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['tariff_forecast']}")


def train_contract_expiry():
    print("\n── [3/3] apex-signal-eprod-contract-expiry · XGBoost multi-class ──")
    train_uri = _upload(TRAIN_DATA_DIR / "contract_expiry_train.csv",
                        f"{PREFIX}/contract_expiry/train.csv")
    val_uri   = _upload(TRAIN_DATA_DIR / "contract_expiry_validation.csv",
                        f"{PREFIX}/contract_expiry/validation.csv")

    img = image_uris.retrieve("xgboost", REGION, version="1.7-1")
    est = Estimator(
        image_uri=img,
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{MODEL_BUCKET}/eprod_contract_expiry/",
        sagemaker_session=sess,
    )
    est.set_hyperparameters(
        objective="multi:softprob",
        num_class=4,
        num_round=120,
        eval_metric="mlogloss",
        max_depth=5,
        eta=0.12,
    )
    est.fit({
        "train":      TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri,   content_type="text/csv"),
    }, wait=True, logs=False)
    est.deploy(
        endpoint_name=ENDPOINTS["contract_expiry"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['contract_expiry']}")


def destroy_all():
    for name in ENDPOINTS.values():
        for op_name, fn in (
            ("endpoint",        lambda n: sm.delete_endpoint(EndpointName=n)),
            ("endpoint_config", lambda n: sm.delete_endpoint_config(EndpointConfigName=n)),
            ("model",           lambda n: sm.delete_model(ModelName=n)),
        ):
            try:
                fn(name)
                print(f"  ✓ deleted {op_name}: {name}")
            except Exception as e:
                msg = getattr(getattr(e, "response", {}), "get", lambda *_: {})("Error", {}).get("Message", str(e))
                print(f"  [skip] {op_name} {name}: {msg}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=list(ENDPOINTS) + ["all"], default="all")
    parser.add_argument("--destroy", action="store_true")
    args = parser.parse_args()

    if args.destroy:
        print("Destroying all EPROD SageMaker endpoints …")
        destroy_all()
        return 0

    _ensure_bucket(TRAIN_BUCKET)
    _ensure_bucket(MODEL_BUCKET)

    pipeline = {
        "vendor_drift":     train_vendor_drift,
        "tariff_forecast":  train_tariff_forecast,
        "contract_expiry":  train_contract_expiry,
    }
    targets = [args.only] if args.only != "all" else list(pipeline)

    t0 = datetime.now(timezone.utc)
    print(f"Region: {REGION}  ·  Role: {ROLE_ARN.split('/')[-1]}")
    print(f"Training bucket: s3://{TRAIN_BUCKET}/{PREFIX}/  ·  Model bucket: s3://{MODEL_BUCKET}/")
    print(f"Targets: {', '.join(targets)}")
    for t in targets:
        pipeline[t]()
    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
    print(f"\nAll endpoints deployed · {elapsed:.0f}s total\n")
    for key in targets:
        name = ENDPOINTS[key]
        print(f"  {key:18s} → arn:aws:sagemaker:{REGION}:{ACCOUNT_ID}:endpoint/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
