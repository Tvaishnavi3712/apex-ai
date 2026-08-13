# ApexLens Sample Files

Real, uploadable files you can drop into **ApexLens** (`/apex-lens`) to test the
end-to-end flow: upload → pipeline selector → 5-stage pipeline → Agent Hub
conversation.

All files live in this folder. Drop any of them into the drop zone or click
**Upload File** in the ApexLens toolbar.

## What's here

| # | File                                       | Size   | Pipeline (auto-selected)          | Demo |
|---|--------------------------------------------|--------|-----------------------------------|------|
| 1 | `01-Order_Mod_Request_1044.pdf`            |  2.7 KB| Zero-Touch Order Modification     | CBB §1 |
| 2 | `02-QC_Batch_50_Certificates.zip`          |   77 KB| QC Batch Ingestion & Hold         | CBB §2 |
| 3 | `03-Port_Strike_Alert_VinylResin.xml`      |  1.5 KB| Disruption Impact & Reroute       | CBB §3 |
| 4 | `04-Invoice_Globex_GLX-2024-0441.pdf`      |  2.7 KB| Invoice Processing & Validation   | — |
| 5 | `05-Claim_CL-8821_WaterDamage.pdf`         |  2.8 KB| Claims Intake & Triage            | — |
| 6 | `06-PO_Acme_4421_Rush.pdf`                 |  2.7 KB| PO Auto-Approval                  | — |
| 7 | `07-QC_Report_Batch_2024-B.pdf`            |  2.6 KB| QC Report Triage                  | — |
| 8 | `08-Contract_GulfCoast_CTR-2026.pdf`       |  2.9 KB| Contract Clause Review            | — |
| 9 | `09-SupplyAlert_VinylResin.xml`            |  0.9 KB| Supply Alert Broadcast            | — |

## How pipeline auto-selection works

When you upload a file, ApexLens opens a pipeline chooser modal. The default
selection is picked by regex-matching the filename in
[`apex-lens.tsx › guessPipelineForFilename`](../frontend/src/pages/apex-lens.tsx):

| Filename contains                                  | Auto-select |
|----------------------------------------------------|-------------|
| `invoice`, `bill`, `receipt`                       | Invoice Processing & Validation |
| `claim`, `fnol`                                    | Claims Intake & Triage |
| `po`, `purchase_order`                             | PO Auto-Approval |
| `qc_batch`, ends with `certificates.zip`           | QC Batch Ingestion & Hold |
| `qc`, `quality`, `defect`                          | QC Report Triage |
| `contract`, `agreement`, `msa`                     | Contract Clause Review |
| `order_mod`, `modification`                        | Zero-Touch Order Modification |
| `port`, `strike`, `disruption`                     | Disruption Impact & Reroute |
| `alert`                                            | Supply Alert Broadcast |

The modal always shows the guess as **RECOMMENDED**; users can override with any
of the other 8 pipelines.

## Regenerating

```bash
cd sample-files
pip install reportlab          # one-time
python3 generate_samples.py
```

The generator rebuilds the whole folder (except this README). It's idempotent —
safe to re-run whenever the demo data needs to change.

## File details

### 1 — Order Modification Request (CBB Demo 1)
Distributor email PDF from Midwest Window & Door Supply requesting a 2" height
increase on order CBB-ORD-1044 (48×60 → 48×62). Variance is +3.3%, within the
5% tolerance, so the pipeline auto-approves.

### 2 — QC Batch Certificates (CBB Demo 2)
ZIP of **50 real QC-certificate PDFs** (one per lot) from Apex Vinyl Solutions
for Ohio Plant 7. 48 pass; two fail:
- **LOT-A44** — tensile strength 36.5 MPa (spec min 38.0)
- **LOT-B12** — color ΔE 2.7 (threshold 2.0)

A `MANIFEST.txt` inside the archive summarizes the batch.

### 3 — Port Strike Alert (CBB Demo 3)
XML alert from Global Supply Chain Monitor about a 7-day strike at the Port of
Savannah affecting Chemours Vinyl Resins (SUP-0044). Contains BOM-traversal
seed data (supplier, material, expected recovery) the pipeline uses to
project $1.09M at risk across 3 plants.

### 4 — Globex Invoice
$87,400 invoice with 3 line items (Widget A, Widget B, expedited freight).
Exceeds the $10k auto-approval threshold → routes to AP Manager Queue.

### 5 — Water Damage FNOL
Claim CL-8821 from Meridian Properties, $142,000 claim value. Triggers senior
adjuster review in the Claims pipeline.

### 6 — Acme Rush PO
PO-4421 · $34,200 · rush delivery · 3 SKUs. All checks pass → auto-approved.

### 7 — Houston QC Batch 2024-B
2,400 units inspected, 19 held (12 surface cracks + 7 dimensional drift).
Partial Hold → routes to Plant Manager.

### 8 — Gulf Coast Vendor Contract
2-year vendor services agreement with non-standard 2%/week penalty clause and
auto-renewal. Routes to Legal Review.

### 9 — Supply Alert XML
Internal alert about 7-day vinyl resin delay affecting 3 plants and 14 SKUs
with $1.09M revenue exposure. Routes to Supply Chain Director + 3 Plant
Managers.
