"""
parse_votes.py — Extract vote tables from City Clerk PDFs using pdfplumber.

Usage:
    python scripts/parse_votes.py data/pdfs/ data/vote_records.json

Reads all PDFs from the input directory and outputs a JSON array of vote records.
"""

import json
import os
import re
import sys
import pdfplumber


def parse_pdf(pdf_path: str) -> list[dict]:
    """Extract vote records from a single City Clerk results PDF."""
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            text = page.extract_text() or ""

            # Try to find the meeting date from the page text
            date_match = re.search(r'(\w+ \d{1,2},? \d{4})', text)
            meeting_date = date_match.group(1) if date_match else "Unknown"

            for table in tables:
                if not table or len(table) < 2:
                    continue
                # Process table rows — adapt this to the actual PDF structure
                # This is a starting template; the actual parsing will depend
                # on the PDF format from the City Clerk's office.
                header = table[0] if table[0] else []
                for row in table[1:]:
                    if not row or not any(row):
                        continue
                    records.append({
                        "date": meeting_date,
                        "item_number": row[0] if len(row) > 0 else "",
                        "item_title": row[1] if len(row) > 1 else "",
                        "raw_row": row,
                        "source_file": os.path.basename(pdf_path),
                    })
    return records


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/parse_votes.py <pdf_dir> <output_json>")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    output_path = sys.argv[2]

    all_records = []
    pdf_files = sorted(f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf'))

    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDFs to process")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"  Parsing: {pdf_file}")
        try:
            records = parse_pdf(pdf_path)
            all_records.extend(records)
        except Exception as e:
            print(f"  ERROR parsing {pdf_file}: {e}")

    print(f"\nExtracted {len(all_records)} total records")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_records, f, indent=2)

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
