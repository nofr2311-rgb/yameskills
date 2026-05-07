#!/usr/bin/env python3
"""HWPX Parser — extracts text and tables from HWPX (ZIP+XML) files."""

import zipfile
import xml.etree.ElementTree as ET
import json
import sys
import os
import re

NAMESPACES = {
    "hp": "http://www.hancom.co.kr/hwpml/2016/HwpMl",
    "hc": "http://www.hancom.co.kr/hwpml/2016/HwpCoreMl",
    "hp11": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs11": "http://www.hancom.co.kr/hwpml/2011/section",
    "hh11": "http://www.hancom.co.kr/hwpml/2011/head",
}

def _find_section_files(zf):
    section_files = []
    for name in zf.namelist():
        lower = name.lower()
        if "section" in lower and lower.endswith(".xml"):
            section_files.append(name)
    section_files.sort(key=lambda x: int(re.findall(r"(\d+)", os.path.basename(x))[-1]) if re.findall(r"(\d+)", os.path.basename(x)) else 0)
    return section_files

def _get_text_recursive(elem):
    texts = []
    if elem.text:
        texts.append(elem.text)
    for child in elem:
        texts.extend(_get_text_recursive(child))
    if elem.tail:
        texts.append(elem.tail)
    return texts

def _local_name(elem):
    tag = elem.tag
    return tag.split("}")[-1] if "}" in tag else tag

def _find_elements(root, tag_local_name):
    results = []
    for prefix, uri in NAMESPACES.items():
        results.extend(root.findall(f".//{{{uri}}}{tag_local_name}"))
    results.extend(root.findall(f".//{tag_local_name}"))
    seen = set()
    unique = []
    for e in results:
        eid = id(e)
        if eid not in seen:
            seen.add(eid)
            unique.append(e)
    return unique

def _parse_table(tbl_elem):
    rows = []
    for row_elem in _find_elements(tbl_elem, "tr"):
        cells = []
        for cell_elem in _find_elements(row_elem, "tc"):
            cell_text = "".join(_get_text_recursive(cell_elem)).strip()
            cells.append(cell_text)
        if cells:
            rows.append(cells)
    return rows

def _walk_elements(elem, results, depth=0):
    local = _local_name(elem)
    if local == "tbl":
        rows = _parse_table(elem)
        if rows:
            results.append({"type": "table", "content": rows})
        return
    if local == "p":
        texts = []
        for t in _find_elements(elem, "t"):
            texts.extend(_get_text_recursive(t))
        text = "".join(texts).strip()
        if text:
            results.append({"type": "paragraph", "content": text})
        for child in elem:
            if _local_name(child) == "tbl":
                _walk_elements(child, results, depth + 1)
        return
    for child in elem:
        _walk_elements(child, results, depth + 1)

def parse_hwpx(filepath):
    result = {"sections": [], "text": "", "tables": [], "metadata": {}}
    try:
        with zipfile.ZipFile(filepath, "r") as zf:
            for mf in [n for n in zf.namelist() if "meta" in n.lower() and n.endswith(".xml")]:
                try:
                    meta_root = ET.fromstring(zf.read(mf).decode("utf-8", errors="replace"))
                    for child in meta_root:
                        key, val = _local_name(child), child.text
                        if val:
                            result["metadata"][key] = val.strip()
                except Exception:
                    pass
            section_files = _find_section_files(zf)
            if not section_files:
                return {"error": "No section files found", "files": zf.namelist()}
            all_text = []
            for sf in section_files:
                try:
                    elements = []
                    _walk_elements(ET.fromstring(zf.read(sf).decode("utf-8", errors="replace")), elements)
                    result["sections"].append({"file": sf, "elements": elements})
                    for e in elements:
                        if e["type"] == "paragraph":
                            all_text.append(e["content"])
                        elif e["type"] == "table":
                            result["tables"].append(e["content"])
                            for row in e["content"]:
                                all_text.append(" | ".join(row))
                except Exception as ex:
                    result["sections"].append({"file": sf, "error": str(ex)})
            result["text"] = "\n".join(all_text)
    except zipfile.BadZipFile:
        result["error"] = "Not a valid HWPX (ZIP) file."
    except Exception as e:
        result["error"] = f"Failed to parse HWPX: {str(e)}"
    return result

def format_output(result):
    lines = []
    if "error" in result:
        return f"[오류] {result['error']}"
    if result.get("metadata"):
        lines.append("=== 문서 정보 ===")
        for k, v in result["metadata"].items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    for i, sec in enumerate(result.get("sections", [])):
        if len(result["sections"]) > 1:
            lines.append(f"=== 섹션 {i+1} ===")
        for e in sec.get("elements", []):
            if e["type"] == "paragraph":
                lines.append(e["content"])
            elif e["type"] == "table":
                lines.append("\n[표]")
                for ri, row in enumerate(e["content"]):
                    lines.append("| " + " | ".join(row) + " |")
                    if ri == 0:
                        lines.append("|" + "|".join(["---"] * len(row)) + "|")
                lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_hwpx.py <file.hwpx> [--json]")
        sys.exit(1)
    result = parse_hwpx(sys.argv[1])
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_output(result))
