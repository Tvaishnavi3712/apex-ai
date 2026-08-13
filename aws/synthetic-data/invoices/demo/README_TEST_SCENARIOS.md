# Invoice Processing Demo - Test Scenarios

## Quick Reference

| # | File | Amount | Expected Result |
|---|------|--------|-----------------|
| 1 | invoice_01_auto_approve.txt | $659.24 | AUTO-APPROVE |
| 2 | invoice_02_manager_approval.txt | $4,925.38 | Manager Approval |
| 3 | invoice_03_director_approval.txt | $34,856.50 | Director Approval |
| 4 | invoice_04_vp_approval.txt | $82,270.00 | VP Finance Approval |
| 5 | invoice_05_missing_po.txt | $4,934.83 | FLAG - Missing PO |
| 6 | invoice_06_new_vendor.txt | $9,581.25 | FLAG - New Vendor |
| 7 | invoice_07_duplicate.txt | $4,925.38 | REJECT - Duplicate |
| 8 | invoice_08_po_mismatch.txt | $17,762.25 | FLAG - PO Mismatch |

---

## Copy-Paste Test Prompts

### Test 1: Auto-Approve (Under $1,000)
```
Process this invoice:
Vendor: QuickPrint Solutions
Invoice #: QPS-2024-0156
Invoice Date: March 10, 2024
PO Number: PO-2024-0089

Line Items:
- Business cards (500 ct) x2 @ $45.00 = $90.00
- Letterhead paper (ream) x5 @ $28.00 = $140.00
- Company brochures (100 ct) x3 @ $85.00 = $255.00
- Envelope printing (box) x2 @ $62.00 = $124.00

Subtotal: $609.00
Tax: $50.24
Total: $659.24
```

### Test 2: Manager Approval ($1K-$10K)
```
Process this invoice:
Vendor: Acme Office Supplies
Invoice #: AOS-2024-0892
Invoice Date: March 11, 2024
PO Number: PO-2024-7834

Line Items:
- Ergonomic Office Chair x10 @ $150.00 = $1,500.00
- Standing Desk - Electric x5 @ $400.00 = $2,000.00
- Monitor Arm - Dual Mount x8 @ $75.00 = $600.00
- Keyboard Tray x10 @ $45.00 = $450.00

Subtotal: $4,550.00
Tax: $375.38
Total: $4,925.38
```

### Test 3: Director Approval ($10K-$50K)
```
Process this invoice:
Vendor: TechServe IT Solutions
Invoice #: TS-2024-3347
Invoice Date: March 12, 2024
PO Number: PO-2024-4521

Line Items:
- Dell PowerEdge Server R750 x2 @ $8,500.00 = $17,000.00
- Cisco Catalyst Switch 9300 x4 @ $2,200.00 = $8,800.00
- APC Smart-UPS 3000VA x2 @ $1,450.00 = $2,900.00
- Installation & Configuration = $3,500.00

Subtotal: $32,200.00
Tax: $2,656.50
Total: $34,856.50
```

### Test 4: VP Finance Approval (Over $50K)
```
Process this invoice:
Vendor: Global Cloud Partners LLC
Invoice #: GCP-2024-0088
Invoice Date: March 12, 2024
PO Number: PO-2024-1001

Line Items:
- Enterprise Cloud Platform License (500 seats) = $45,000.00
- Premium Support Package (24/7) = $12,000.00
- Data Migration Services = $8,500.00
- Security & Compliance Add-on = $6,500.00
- Training (40 hours) = $4,000.00

Subtotal: $76,000.00
Tax: $6,270.00
Total: $82,270.00
```

### Test 5: Missing PO (Exception)
```
Process this invoice:
Vendor: Metro Catering Services
Invoice #: MCS-2024-0445
Invoice Date: March 8, 2024
PO Number: NOT PROVIDED

Line Items:
- Corporate Event Catering (75 guests) = $2,800.00
- Premium Beverage Package = $650.00
- Event Setup & Breakdown = $400.00
- Gratuity (18%) = $693.00

Subtotal: $4,543.00
Tax: $391.83
Total: $4,934.83

Note: This was for the Q1 All-Hands meeting on March 5th
```

### Test 6: New Vendor (Not in System)
```
Process this invoice:
Vendor: Bright Ideas Marketing Agency
Invoice #: BI-2024-0012
Invoice Date: March 11, 2024
PO Number: PO-2024-8899

This is a NEW VENDOR - first time doing business with them.

Line Items:
- Brand Strategy Workshop = $3,500.00
- Logo Design Package = $2,500.00
- Brand Guidelines Document = $1,800.00
- Social Media Templates (10) = $950.00

Subtotal: $8,750.00
Tax: $831.25
Total: $9,581.25
```

### Test 7: Duplicate Invoice
```
Process this invoice:
Vendor: Acme Office Supplies
Invoice #: AOS-2024-0892
Invoice Date: March 11, 2024
PO Number: PO-2024-7834

Line Items:
- Ergonomic Office Chair x10 @ $150.00 = $1,500.00
- Standing Desk - Electric x5 @ $400.00 = $2,000.00

Total: $4,925.38

Note: Vendor says this is a resend, please process urgently.
```

### Test 8: PO Amount Mismatch
```
Process this invoice:
Vendor: DataPro Analytics Inc.
Invoice #: DPA-2024-0234
Invoice Date: March 10, 2024
PO Number: PO-2024-5500

Original PO was for $12,000.00

Line Items:
- Data Analytics Platform License = $9,500.00
- Additional User Seats (25) = $3,000.00
- API Integration Package = $2,500.00
- Rush Implementation Fee = $1,500.00 (added per verbal approval)

Subtotal: $16,500.00
Tax: $1,262.25
Total: $17,762.25

Note: Rush fee was verbally approved by project manager
```

---

## Approval Thresholds

| Amount Range | Approver | Workflow |
|--------------|----------|----------|
| Under $1,000 | Auto-Approve | None |
| $1,000 - $10,000 | Manager | Standard |
| $10,000 - $50,000 | Director | Elevated |
| Over $50,000 | VP Finance | Executive |

## Exception Scenarios

| Scenario | Action |
|----------|--------|
| Missing PO (>$1K) | Flag for review |
| New Vendor | Route to vendor onboarding |
| Duplicate Invoice | Reject automatically |
| PO Mismatch (>5%) | Route to Purchasing Manager |
