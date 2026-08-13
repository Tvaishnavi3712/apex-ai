#!/usr/bin/env python3
"""
Verizon Far Edge — generate training data for the 3 SageMaker endpoints:
  • apex-signal-vz-wave-risk        (XGBoost binary)
  • apex-signal-vz-site-cert        (XGBoost binary)
  • apex-signal-vz-thermal-anomaly  (Random Cut Forest)

Inputs (already in repo):
  inventory/verizon_site_inventory_wave1.csv      (16,247 sites)
  inventory/historical_failure_patterns.csv       (1,296 historical waves)

Outputs (written here, then uploaded by deploy_sagemaker_vz_endpoints.py):
  ml_training/wave_risk_train.csv
  ml_training/wave_risk_validation.csv
  ml_training/site_cert_train.csv
  ml_training/site_cert_validation.csv
  ml_training/thermal_telemetry.jsonl

Run:
  python3 synthetic-data/verizon_far_edge/generate_ml_training_data.py

Idempotent — safe to re-run.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
INV_CSV  = ROOT / "inventory" / "verizon_site_inventory_wave1.csv"
HIST_CSV = ROOT / "inventory" / "historical_failure_patterns.csv"
OUT_DIR  = ROOT / "ml_training"
OUT_DIR.mkdir(exist_ok=True)

# Canonical enums shared with backend/services/sagemaker.py
DEVICE_ENUM  = {"CaaS-Node-Type-A": 0, "CaaS-Node-Type-B": 1, "CaaS-Node-Type-C": 2}
REGION_ENUM  = {
    "Northeast": 0, "Northwest": 1, "Southeast": 2, "Southwest": 3,
    "Midwest":   4, "South_Central": 5,
}
SLA_ENUM     = {"premium": 0, "standard": 1, "economy": 2}
STATUS_ENUM  = {"PASS": 0, "CONDITIONAL_PASS": 1, "FAIL": 2}


def _firmware_jump(a: str, b: str) -> int:
    """Counts minor-version gap. '23.06' → '24.01' is 4 (skip-level)."""
    try:
        ay, am = [int(x) for x in a.split(".")]
        by, bm = [int(x) for x in b.split(".")]
        return max(0, (by - ay) * 6 + (bm - am) // 2)
    except Exception:
        return 1


# ──────────────────────────── 1 · wave-risk ────────────────────────────

def build_wave_risk() -> tuple[Path, Path]:
    """XGBoost binary: P(outage occurs within 30 days of wave deploy).

    Source: historical_failure_patterns.csv (1,296 real wave records with
    outage_occurred labels and per-wave features).
    """
    df = pd.read_csv(HIST_CSV)
    df["cycle_date"]    = pd.to_datetime(df["cycle_date"])
    df["device_enc"]    = df["device_type"].map(DEVICE_ENUM).fillna(1).astype(int)
    df["region_enc"]    = df["region"].map(REGION_ENUM).fillna(0).astype(int)
    df["jump"]          = df.apply(lambda r: _firmware_jump(r["firmware_from"], r["firmware_to"]), axis=1)
    df["season_q"]      = ((df["cycle_date"].dt.month - 1) // 3 + 1).astype(int)
    # synthesize per-row wave_size — historical patterns don't carry it, so we
    # bucket by device type (Type-A ≈ 7k, Type-B ≈ 6k, Type-C ≈ 3k sites)
    rng = np.random.default_rng(42)
    sz_map = {"CaaS-Node-Type-A": 7000, "CaaS-Node-Type-B": 6000, "CaaS-Node-Type-C": 3000}
    df["wave_size"] = df["device_type"].map(sz_map).fillna(5000).astype(int)
    df["wave_size"] = (df["wave_size"] * rng.uniform(0.85, 1.15, len(df))).astype(int)

    df["label"] = df["outage_occurred"].astype(bool).astype(int)

    cols = [
        "label",
        "device_enc", "jump", "region_enc",
        "schema_drift_events", "test_pass_rate",
        "season_q", "wave_size",
    ]
    out = df[cols].dropna()
    out = out.sample(frac=1.0, random_state=42).reset_index(drop=True)
    split = int(len(out) * 0.8)

    train_path = OUT_DIR / "wave_risk_train.csv"
    val_path   = OUT_DIR / "wave_risk_validation.csv"
    out.iloc[:split].to_csv(train_path, index=False, header=False)
    out.iloc[split:].to_csv(val_path,   index=False, header=False)
    print(f"  ✓ wave_risk: {split} train / {len(out)-split} val · "
          f"positive rate {out['label'].mean()*100:.1f}%")
    return train_path, val_path


# ──────────────────────────── 2 · site-cert ────────────────────────────

def build_site_cert() -> tuple[Path, Path]:
    """XGBoost binary: P(site fails the next 247-test cert cycle).

    Source: verizon_site_inventory_wave1.csv (16,247 real-shape sites). The
    label is *synthesized* from the existing risk_score column (continuous
    0..1) with realistic noise, since the inventory doesn't carry direct
    pass/fail outcomes. risk_score already correlates with device_age,
    incident history, firmware jump — so the model learns the underlying
    feature → risk relationship the inventory was built with.
    """
    df = pd.read_csv(INV_CSV)
    df["device_enc"]            = df["device_type"].map(DEVICE_ENUM).fillna(1).astype(int)
    df["region_enc"]            = df["region"].map(REGION_ENUM).fillna(0).astype(int)
    df["sla_enc"]               = df["vendor_sla_tier"].map(SLA_ENUM).fillna(1).astype(int)
    df["status_enc"]            = df["last_cert_status"].map(STATUS_ENUM).fillna(1).astype(int)
    df["jump"]                  = df.apply(
        lambda r: _firmware_jump(r["current_firmware"], r["target_firmware"]), axis=1
    )
    # prior_drift_exposure synthesized from incident count clipped + a small
    # device-class adjustment (Type-B carries more drift exposure)
    df["prior_drift_exposure"]  = (
        df["incident_count_12m"].clip(0, 5) +
        (df["device_enc"] == 1).astype(int)
    )

    # Label: turn the continuous risk_score into a noisy binary fail label
    # so the demo shows ~12% fail rate (industry typical for Type-B waves).
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.07, len(df))
    df["label"] = ((df["risk_score"] + noise) >= 0.72).astype(int)

    cols = [
        "label",
        "device_age_months", "incident_count_12m", "status_enc",
        "jump", "sla_enc", "region_enc", "prior_drift_exposure",
    ]
    out = df[cols].dropna()
    out = out.sample(frac=1.0, random_state=7).reset_index(drop=True)
    split = int(len(out) * 0.8)

    train_path = OUT_DIR / "site_cert_train.csv"
    val_path   = OUT_DIR / "site_cert_validation.csv"
    out.iloc[:split].to_csv(train_path, index=False, header=False)
    out.iloc[split:].to_csv(val_path,   index=False, header=False)
    print(f"  ✓ site_cert: {split} train / {len(out)-split} val · "
          f"positive rate {out['label'].mean()*100:.1f}%")
    return train_path, val_path


# ──────────────────── 3 · thermal-anomaly (RCF) ─────────────────────────

def build_thermal_telemetry() -> Path:
    """Random Cut Forest training data.

    Generates ~10,000 thermal-reading time series. Each row is a (timestamp,
    site_id, thermal_c, fan_rpm, cpu_load, ambient_c) snapshot. We seed a
    realistic baseline distribution (NE sites slightly hotter due to higher
    rack density), inject a small fraction of anomalous sites with thermal
    cluster events, and emit unlabelled — RCF is unsupervised so it only
    needs the feature columns.

    Output format: SageMaker RCF wants a CSV (no header) with all numeric
    feature columns; we use a 4-dimensional vector per record.
    """
    rng = np.random.default_rng(99)
    n_sites    = 200
    pts_per    = 24 * 7              # one week of hourly samples per site
    total      = n_sites * pts_per

    # Baselines
    base_temp  = rng.uniform(28, 38, n_sites)        # cabinet temp degC
    base_fan   = rng.uniform(2500, 4200, n_sites)    # rpm
    base_load  = rng.uniform(0.3, 0.7, n_sites)      # cpu_load 0..1

    # Inject 8% of sites with a thermal anomaly cluster
    anomaly_sites = rng.choice(n_sites, size=int(0.08 * n_sites), replace=False)

    rows = []
    for s in range(n_sites):
        temp_curve = base_temp[s] + rng.normal(0, 1.4, pts_per)
        fan_curve  = base_fan[s]  + rng.normal(0, 120, pts_per)
        load_curve = np.clip(base_load[s] + rng.normal(0, 0.05, pts_per), 0.1, 0.95)
        amb_curve  = rng.uniform(20, 26, pts_per)

        if s in anomaly_sites:
            # Anomaly window: hours 96-128 with temp + load spikes
            start = rng.integers(60, pts_per - 40)
            window = slice(start, start + rng.integers(8, 28))
            temp_curve[window] += rng.uniform(7, 14)
            load_curve[window] = np.clip(load_curve[window] + rng.uniform(0.2, 0.35), 0, 1)
            fan_curve[window] += rng.uniform(800, 1500)

        for i in range(pts_per):
            rows.append((temp_curve[i], fan_curve[i], load_curve[i], amb_curve[i]))

    df = pd.DataFrame(rows, columns=["thermal_c", "fan_rpm", "cpu_load", "ambient_c"])
    out_path = OUT_DIR / "thermal_telemetry.csv"
    df.to_csv(out_path, index=False, header=False)
    print(f"  ✓ thermal_telemetry: {len(df):,} rows ({n_sites} sites × {pts_per} hrs) · "
          f"{len(anomaly_sites)} anomalous sites")
    return out_path


def main():
    print(f"Generating Verizon Far Edge ML training data → {OUT_DIR}")
    print(f"  Inputs: {INV_CSV.name} ({sum(1 for _ in open(INV_CSV))-1:,} sites)")
    print(f"          {HIST_CSV.name} ({sum(1 for _ in open(HIST_CSV))-1:,} historical waves)")
    print("")
    build_wave_risk()
    build_site_cert()
    build_thermal_telemetry()
    print("")
    print("Done. Upload + train + deploy with:")
    print("  python3 backend/scripts/deploy_sagemaker_vz_endpoints.py")


if __name__ == "__main__":
    main()
