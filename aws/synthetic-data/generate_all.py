#!/usr/bin/env python3
"""
Generate All Synthetic Data
Master script to generate all document types for testing
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add generators to path
sys.path.insert(0, os.path.dirname(__file__))

from generators.invoice_generator import generate_invoice_batch
from generators.receipt_generator import generate_receipt_batch
from generators.bank_statement_generator import generate_statement_batch


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic financial documents")
    parser.add_argument("--invoices", type=int, default=10, help="Number of invoices to generate")
    parser.add_argument("--receipts", type=int, default=20, help="Number of receipts to generate")
    parser.add_argument("--statements", type=int, default=6, help="Number of bank statements to generate")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDFs (requires weasyprint)")

    args = parser.parse_args()

    output_dir = os.path.join(os.path.dirname(__file__), args.output)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("CBTS Apex AI Platform - Synthetic Data Generator")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print()

    results = {
        "generated_at": datetime.now().isoformat(),
        "output_directory": output_dir,
        "documents": {}
    }

    # Generate invoices
    if args.invoices > 0:
        print(f"\n[1/3] Generating {args.invoices} invoices...")
        invoice_dir = os.path.join(output_dir, "invoices")
        invoice_manifest = generate_invoice_batch(args.invoices, invoice_dir)
        results["documents"]["invoices"] = {
            "count": len(invoice_manifest),
            "directory": "invoices",
            "manifest": "invoices/manifest.json"
        }
        print(f"      Generated {len(invoice_manifest)} invoices")

    # Generate receipts
    if args.receipts > 0:
        print(f"\n[2/3] Generating {args.receipts} receipts...")
        receipt_dir = os.path.join(output_dir, "receipts")
        receipt_manifest = generate_receipt_batch(args.receipts, receipt_dir)
        results["documents"]["receipts"] = {
            "count": len(receipt_manifest),
            "directory": "receipts",
            "manifest": "receipts/manifest.json"
        }
        print(f"      Generated {len(receipt_manifest)} receipts")

    # Generate bank statements
    if args.statements > 0:
        print(f"\n[3/3] Generating {args.statements} bank statements...")
        statement_dir = os.path.join(output_dir, "statements")
        statement_manifest = generate_statement_batch(args.statements, statement_dir)
        results["documents"]["statements"] = {
            "count": len(statement_manifest),
            "directory": "statements",
            "manifest": "statements/manifest.json"
        }
        print(f"      Generated {len(statement_manifest)} statements")

    # Generate PDFs if requested
    if args.pdf:
        print("\n[PDF] Converting HTML to PDF...")
        try:
            from weasyprint import HTML

            for doc_type in ["invoices", "receipts", "statements"]:
                html_dir = os.path.join(output_dir, doc_type, "html")
                pdf_dir = os.path.join(output_dir, doc_type, "pdf")

                if os.path.exists(html_dir):
                    os.makedirs(pdf_dir, exist_ok=True)

                    for html_file in os.listdir(html_dir):
                        if html_file.endswith(".html"):
                            html_path = os.path.join(html_dir, html_file)
                            pdf_path = os.path.join(pdf_dir, html_file.replace(".html", ".pdf"))
                            HTML(filename=html_path).write_pdf(pdf_path)

                    print(f"      Converted {doc_type} to PDF")

        except ImportError:
            print("      Warning: weasyprint not installed. Skipping PDF generation.")
            print("      Install with: pip install weasyprint")

    # Save master manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"Total documents: {sum(d.get('count', 0) for d in results['documents'].values())}")
    print(f"Master manifest: {manifest_path}")
    print()

    return results


if __name__ == "__main__":
    main()
