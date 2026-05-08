#!/usr/bin/env python3
"""Build maintenance-report JSON from online/phone support PDFs."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import pdfplumber


def pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def split_entries(text: str) -> list[str]:
    chunks = re.split(r"\n(?=\d{4}[-.]\d{1,2}[-.]\d{1,2}|\d+\s+\d{4}[-.]\d{1,2}[-.]\d{1,2})", text)
    return [c.strip() for c in chunks if len(c.strip()) > 20]


def parse_online(path: Path) -> list[dict[str, str]]:
    entries = []
    for chunk in split_entries(pdf_text(path)):
        date_match = re.search(r"(\d{4}[-.]\d{1,2}[-.]\d{1,2})", chunk)
        if not date_match:
            continue
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        title = next((line for line in lines if line != date_match.group(1)), lines[0])
        entries.append(
            {
                "date": date_match.group(1).replace(".", "-"),
                "title": title[:80],
                "question": chunk[:800],
                "answer": "처리 내용 확인 필요",
            }
        )
    return entries[:50]


def parse_phone(path: Path) -> list[dict[str, str]]:
    rows = []
    for index, chunk in enumerate(split_entries(pdf_text(path)), start=1):
        date_match = re.search(r"(\d{4}[-.]\d{1,2}[-.]\d{1,2})", chunk)
        if not date_match:
            continue
        rows.append(
            {
                "no": str(index),
                "date": date_match.group(1).replace("-", "."),
                "gubun": "유선상담",
                "content": chunk[:500],
                "answer": "처리 내용 확인 필요",
                "category": "기타",
            }
        )
    return rows[:80]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--online-pdf", required=True)
    parser.add_argument("--phone-pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--year", default=str(date.today().year))
    parser.add_argument("--prev-month", default="04월")
    parser.add_argument("--month", default="05월")
    parser.add_argument("--report-date", default=date.today().strftime("%Y-%m-%d"))
    args = parser.parse_args()

    data = {
        "year": args.year,
        "prev_month": args.prev_month,
        "month": args.month,
        "report_date": args.report_date,
        "online": parse_online(Path(args.online_pdf)),
        "phone": parse_phone(Path(args.phone_pdf)),
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"online={len(data['online'])}")
    print(f"phone={len(data['phone'])}")
    print(f"created={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
