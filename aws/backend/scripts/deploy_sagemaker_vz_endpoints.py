#!/usr/bin/env python3
"""
Train + deploy the 3 Verizon Far Edge SageMaker endpoints onto AWS us-east-1.

  apex-signal-vz-wave-risk       — XGBoost binary (wave outage prediction)
  apex-signal-vz-site-cert       — XGBoost binary (per-site cert pre-flight risk)
  apex-signal-vz-thermal-anomaly — Random Cut Forest (NE thermal anomaly detect)

Training data is built by:
  synthetic-data/verizon_far_edge/generate_ml_training_data.py
which writes CSVs to synthetic-data/verizon_far_edge/ml_training/.

This script:
  1. Uploads each training CSV to s3://apex-ml-training-data-{ACCT}/verizon/
  2. Trains the model on SageMaker
  3. Deploys to a managed endpoint with the canonical name
  4. Prints the endpoint ARNs

Cost: 3 × ml.m5.large ≈ $7/day. Tear down with `--destroy`.

Run:
  cd backend && source venv/bin/activate
  python3 scripts/deploy_sagemaker_vz_endpoints.py            # all 3
  python3 scripts/deploy_sagemaker_vz_endpoints.py --only wave_risk
  python3 scripts/deploy_sagemaker_vz_endpoints.py --destroy

Prereqs:
  - synthetic-data/verizon_far_edge/ml_training/*.csv exist
  - AWS creds have sagemaker:* + s3:* on the two buckets
  - The IAM role below exists (it already does, used by supply-chain script)
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
PREFIX       = "verizon"

INSTANCE_TYPE  = "ml.m5.large"
INSTANCE_COUNT = 1

ENDPOINTS = {
    "wave_risk":       "apex-signal-vz-wave-risk",
    "site_cert":       "apex-signal-vz-site-cert",
    "thermal_anomaly": "apex-signal-vz-thermal-anomaly",
}

REPO_ROOT     = Path(__file__).resolve().parents[2]
TRAIN_DATA_DIR = REPO_ROOT / "synthetic-data" / "verizon_far_edge" / "ml_training"

s3   = boto3.client("s3", region_name=REGION)
sm   = boto3.client("sagemaker", region_name=REGION)
sess = Session(boto3.session.Session(region_name=REGION))


# ──────────────────────────── helpers ────────────────────────────

def _upload(local_path: Path, s3_key: str) -> str:
    if not local_path.exists():
        sys.exit(f"  ✗ missing training file: {local_path}\n"
                 f"    Run synthetic-data/verizon_far_edge/generate_ml_training_data.py first.")
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

def train_wave_risk():
    print("\n── [1/3] apex-signal-vz-wave-risk · XGBoost binary ──")
    train_uri = _upload(TRAIN_DATA_DIR / "wave_risk_train.csv",
                        f"{PREFIX}/wave_risk/train.csv")
    val_uri   = _upload(TRAIN_DATA_DIR / "wave_risk_validation.csv",
                        f"{PREFIX}/wave_risk/validation.csv")

    img = image_uris.retrieve("xgboost", REGION, version="1.7-1")
    est = Estimator(
        image_uri=img,
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{MODEL_BUCKET}/vz_wave_risk/",
        sagemaker_session=sess,
    )
    # scale_pos_weight = N_neg / N_pos handles the ~1% positive class
    est.set_hyperparameters(
        objective="binary:logistic",
        num_round=80,
        eval_metric="auc",
        max_depth=4,
        eta=0.15,
        scale_pos_weight=80,
    )
    est.fit({
        "train":      TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri,   content_type="text/csv"),
    }, wait=True, logs=False)
    est.deploy(
        endpoint_name=ENDPOINTS["wave_risk"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['wave_risk']}")


def train_site_cert():
    print("\n── [2/3] apex-signal-vz-site-cert · XGBoost binary ──")
    train_uri = _upload(TRAIN_DATA_DIR / "site_cert_train.csv",
                        f"{PREFIX}/site_cert/train.csv")
    val_uri   = _upload(TRAIN_DATA_DIR / "site_cert_validation.csv",
                        f"{PREFIX}/site_cert/validation.csv")

    img = image_uris.retrieve("xgboost", REGION, version="1.7-1")
    est = Estimator(
        image_uri=img,
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{MODEL_BUCKET}/vz_site_cert/",
        sagemaker_session=sess,
    )
    est.set_hyperparameters(
        objective="binary:logistic",
        num_round=120,
        eval_metric="auc",
        max_depth=5,
        eta=0.12,
        scale_pos_weight=47,
    )
    est.fit({
        "train":      TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri,   content_type="text/csv"),
    }, wait=True, logs=False)
    est.deploy(
        endpoint_name=ENDPOINTS["site_cert"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['site_cert']}")


def train_thermal_anomaly():
    """Use the high-level RandomCutForest SDK class. It auto-converts the
    numpy array to RecordIO-protobuf (RCF's native format) so we sidestep
    the CSV/content-type validation gymnastics required by the low-level
    Estimator path."""
    print("\n── [3/3] apex-signal-vz-thermal-anomaly · Random Cut Forest ──")
    csv_path = TRAIN_DATA_DIR / "thermal_telemetry.csv"
    if not csv_path.exists():
        sys.exit(f"  ✗ missing {csv_path}")

    import numpy as np
    from sagemaker import RandomCutForest

    print(f"    ↑ loading {csv_path.name}")
    data = np.loadtxt(str(csv_path), delimiter=",")
    print(f"    ↑ training matrix shape: {data.shape}")

    rcf = RandomCutForest(
        role=ROLE_ARN,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        data_location=f"s3://{TRAIN_BUCKET}/{PREFIX}/thermal_anomaly_rcf/",
        output_path=f"s3://{MODEL_BUCKET}/vz_thermal_anomaly/",
        num_samples_per_tree=256,
        num_trees=100,
        sagemaker_session=sess,
    )
    rcf.fit(rcf.record_set(data.astype("float32")), wait=True, logs=False)
    rcf.deploy(
        endpoint_name=ENDPOINTS["thermal_anomaly"],
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
    )
    print(f"  ✓ deployed: {ENDPOINTS['thermal_anomaly']}")


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
        print("Destroying all Verizon Far Edge SageMaker endpoints …")
        destroy_all()
        return 0

    _ensure_bucket(TRAIN_BUCKET)
    _ensure_bucket(MODEL_BUCKET)

    pipeline = {
        "wave_risk":       train_wave_risk,
        "site_cert":       train_site_cert,
        "thermal_anomaly": train_thermal_anomaly,
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
