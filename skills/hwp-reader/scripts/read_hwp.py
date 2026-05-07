#!/usr/bin/env python3
"""HWP/HWPX Reader — auto-detects format and extracts content."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_hwpx import parse_hwpx, format_output as fmt_hwpx
from parse_hwp import parse_hwp, format_output as fmt_hwp

def detect_format(fp):
    with open(fp, "rb") as f: m = f.read(8)
    if m[:4] == b"PK\x03\x04": return "hwpx"
    if m[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1": return "hwp"
    return "unknown"

def read_document(fp, output_json=False, tables_only=False):
    if not os.path.exists(fp): return f"[오류] 파일 없음: {fp}"
    fmt = detect_format(fp)
    if fmt == "unknown":
        ext = os.path.splitext(fp)[1].lower()
        fmt = "hwpx" if ext == ".hwpx" else "hwp" if ext == ".hwp" else None
    if not fmt: return "[오류] 지원되지 않는 형식. HWP 또는 HWPX 파일을 제공해주세요."
    result = parse_hwpx(fp) if fmt == "hwpx" else parse_hwp(fp)
    formatter = fmt_hwpx if fmt == "hwpx" else fmt_hwp
    if tables_only:
        tables = result.get("tables", [])
        for s in result.get("sections", []):
            for e in s.get("elements", []):
                if e.get("type") == "table": tables.append(e["content"])
        if output_json: return json.dumps({"tables": tables}, ensure_ascii=False, indent=2)
        if not tables: return "[정보] 표를 찾지 못했습니다."
        lines = []
        for i, t in enumerate(tables):
            lines.append(f"=== 표 {i+1} ===")
            for ri, row in enumerate(t):
                lines.append("| " + " | ".join(row) + " |")
                if ri == 0: lines.append("|" + "|".join(["---"]*len(row)) + "|")
            lines.append("")
        return "\n".join(lines)
    if output_json: return json.dumps(result, ensure_ascii=False, indent=2)
    return formatter(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_hwp.py <file> [--json] [--tables-only]"); sys.exit(1)
    print(read_document(sys.argv[1], "--json" in sys.argv, "--tables-only" in sys.argv))
