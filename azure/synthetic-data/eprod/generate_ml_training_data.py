#!/usr/bin/env python3
"""
EPROD — generate training data for the 3 Azure ML endpoints:
  • apex-signal-eprod-vendor-drift     (XGBoost regression)
  • apex-signal-eprod-tariff-forecast  (XGBoost regression)
  • apex-signal-eprod-contract-expiry  (XGBoost multi-class classification)

Outputs (written here, then uploaded by deploy_azure_ml_eprod_endpoints.py):
  ml_training/vendor_drift_train.csv      + vendor_drift_validation.csv
  ml_training/tariff_forecast_train.csv   + tariff_forecast_validation.csv
  ml_training/contract_expiry_train.csv   + contract_expiry_validation.csv

All CSVs are headerless, label-first column (Azure ML XGBoost convention).
Deterministic via numpy.random.default_rng(42).

Run:
  python3 synthetic-data/eprod/generate_ml_training_data.py

Idempotent — safe to re-run.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "ml_training"
OUT_DIR.mkdir(exist_ok=True)


# ──────────────────────── 1 · vendor-drift (regression) ────────────────────────

def build_vendor_drift() -> tuple[Path, Path]:
    """XGBoost regression: projected next-90-day vendor pricing drift %.

    Features:
      trailing_3mo_drift_pct, trailing_6mo_drift_pct, vendor_tenure_months,
      industry_segment_enc, msa_renewal_count, total_spend_log

    Label (continuous):
      next_90day_drift_pct (correlates positively with trailing drifts and
      msa_renewal_count — more renewals → more accumulated price escalation).
    """
    rng = np.random.default_rng(42)
    n = 1000

    trailing_3mo  = rng.normal(2.0, 2.5, n).clip(-4, 12)
    trailing_6mo  = trailing_3mo * 0.7 + rng.normal(1.5, 2.0, n).clip(-5, 14)
    tenure_months = rng.integers(6, 240, n)
    industry_enc  = rng.integers(0, 6, n)        # 6 industry segments
    msa_renewals  = rng.integers(0, 8, n)
    spend_log     = rng.normal(13.5, 1.4, n).clip(10, 18)  # log($ annual spend)

    # Synthesize label with signal + noise
    label = (
        0.55 * trailing_3mo
        + 0.30 * trailing_6mo
        + 0.45 * msa_renewals
        + 0.04 * (spend_log - 13.5)
        - 0.003 * (tenure_months - 120)
        + 0.10 * (industry_enc - 2.5)
        + rng.normal(0, 0.9, n)
    )
    label = np.round(label, 2)

    df = pd.DataFrame({
        "label": label,
        "trailing_3mo_drift_pct": np.round(trailing_3mo, 2),
        "trailing_6mo_drift_pct": np.round(trailing_6mo, 2),
        "vendor_tenure_months":   tenure_months,
        "industry_segment_enc":   industry_enc,
        "msa_renewal_count":      msa_renewals,
        "total_spend_log":        np.round(spend_log, 3),
    })
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    split = int(len(df) * 0.8)

    train_path = OUT_DIR / "vendor_drift_train.csv"
    val_path   = OUT_DIR / "vendor_drift_validation.csv"
    df.iloc[:split].to_csv(train_path, index=False, header=False)
    df.iloc[split:].to_csv(val_path,   index=False, header=False)
    print(f"  ✓ vendor_drift: {split} train / {len(df)-split} val · "
          f"label range [{df['label'].min():.2f}, {df['label'].max():.2f}] "
          f"mean {df['label'].mean():.2f}")
    return train_path, val_path


# ──────────────────────── 2 · tariff-forecast (regression) ────────────────────────

def build_tariff_forecast() -> tuple[Path, Path]:
    """XGBoost regression: projected_rate_change_pct for natural-gas pipeline
    tariffs. Strong correlation with ppi_fg_yoy_change_pct.

    Features:
      current_rate_per_dth, prior_year_rate, ppi_fg_index, ppi_fg_yoy_change_pct,
      commodity_enc, region_enc, pipeline_tenure_years, surcharge_history_avg
    """
    rng = np.random.default_rng(42)
    n = 800

    current_rate    = rng.uniform(0.45, 2.80, n)
    prior_year_rate = current_rate * rng.uniform(0.92, 1.04, n)
    ppi_fg_index    = rng.uniform(245, 295, n)
    ppi_fg_yoy      = rng.normal(3.4, 1.8, n).clip(-2, 9)
    commodity_enc   = rng.integers(0, 4, n)      # gas/oil/NGL/water
    region_enc      = rng.integers(0, 7, n)      # 7 FERC regions
    tenure_years    = rng.uniform(1, 35, n)
    surcharge_avg   = rng.normal(0.6, 0.4, n).clip(0, 2.5)

    # Label: projected % change strongly tied to PPI-FG YoY
    label = (
        0.85 * ppi_fg_yoy
        + 0.30 * surcharge_avg
        + 0.04 * (current_rate - prior_year_rate) / current_rate.clip(0.1) * 100
        + 0.02 * (region_enc - 3)
        - 0.005 * (tenure_years - 17)
        + rng.normal(0, 0.55, n)
    )
    label = np.round(label, 2)

    df = pd.DataFrame({
        "label": label,
        "current_rate_per_dth":     np.round(current_rate, 4),
        "prior_year_rate":          np.round(prior_year_rate, 4),
        "ppi_fg_index":             np.round(ppi_fg_index, 2),
        "ppi_fg_yoy_change_pct":    np.round(ppi_fg_yoy, 2),
        "commodity_enc":            commodity_enc,
        "region_enc":               region_enc,
        "pipeline_tenure_years":    np.round(tenure_years, 1),
        "surcharge_history_avg":    np.round(surcharge_avg, 3),
    })
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    split = int(len(df) * 0.8)

    train_path = OUT_DIR / "tariff_forecast_train.csv"
    val_path   = OUT_DIR / "tariff_forecast_validation.csv"
    df.iloc[:split].to_csv(train_path, index=False, header=False)
    df.iloc[split:].to_csv(val_path,   index=False, header=False)
    print(f"  ✓ tariff_forecast: {split} train / {len(df)-split} val · "
          f"label range [{df['label'].min():.2f}, {df['label'].max():.2f}] "
          f"mean {df['label'].mean():.2f}")
    return train_path, val_path


# ──────────────────────── 3 · contract-expiry (multi-class) ────────────────────────

def build_contract_expiry() -> tuple[Path, Path]:
    """XGBoost multi-class: contract expiry risk tier (0=low ... 3=critical).

    Risk rises sharply with low days_to_expiry × high spend × no renewal.

    Features:
      days_to_expiry, annual_spend_log, scope_lines, renewal_initiated_int (0/1),
      complexity_enc (0/1/2 low/med/high), contract_type_enc (0/1/2/3
      MSA/ROW/Service/Tariff), vendor_tenure_years
    """
    rng = np.random.default_rng(42)
    n = 1500

    days_to_expiry      = rng.integers(0, 540, n)
    annual_spend_log    = rng.normal(13.0, 1.6, n).clip(9, 18)
    scope_lines         = rng.integers(1, 50, n)
    renewal_initiated   = rng.integers(0, 2, n)
    complexity_enc      = rng.integers(0, 3, n)
    contract_type_enc   = rng.integers(0, 4, n)
    vendor_tenure_years = rng.uniform(0.5, 30, n)

    # Risk score: low days_to_expiry + high spend + no renewal => high risk
    risk_score = (
        (180 - days_to_expiry.clip(0, 180)) / 180.0 * 3.0    # 0..3 (worse as expiry nears)
        + (annual_spend_log - 12.0).clip(0, 6) * 0.35        # high spenders escalate faster
        + (1 - renewal_initiated) * 1.4                      # no renewal initiated → +1.4
        + complexity_enc * 0.25
        + (contract_type_enc == 0).astype(int) * 0.30        # MSA = higher stakes
        - (vendor_tenure_years / 30.0) * 0.20                # long tenure dampens risk
        + rng.normal(0, 0.35, n)
    )

    # Bucket into 4 tiers: 0 low, 1 medium, 2 high, 3 critical
    label = np.zeros(n, dtype=int)
    label[risk_score >= 1.2]  = 1
    label[risk_score >= 2.4]  = 2
    label[risk_score >= 3.6]  = 3

    df = pd.DataFrame({
        "label": label,
        "days_to_expiry":         days_to_expiry,
        "annual_spend_log":       np.round(annual_spend_log, 3),
        "scope_lines":            scope_lines,
        "renewal_initiated_int":  renewal_initiated,
        "complexity_enc":         complexity_enc,
        "contract_type_enc":      contract_type_enc,
        "vendor_tenure_years":    np.round(vendor_tenure_years, 1),
    })
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    split = int(len(df) * 0.8)

    train_path = OUT_DIR / "contract_expiry_train.csv"
    val_path   = OUT_DIR / "contract_expiry_validation.csv"
    df.iloc[:split].to_csv(train_path, index=False, header=False)
    df.iloc[split:].to_csv(val_path,   index=False, header=False)

    counts = df["label"].value_counts().sort_index().to_dict()
    print(f"  ✓ contract_expiry: {split} train / {len(df)-split} val · "
          f"class distribution {counts}")
    return train_path, val_path


def main():
    print(f"Generating EPROD ML training data → {OUT_DIR}")
    print("")
    build_vendor_drift()
    build_tariff_forecast()
    build_contract_expiry()
    print("")
    print("Done. Upload + train + deploy with:")
    print("  python3 backend/scripts/deploy_azure_ml_eprod_endpoints.py")


if __name__ == "__main__":
    main()
