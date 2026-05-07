#!/usr/bin/env python3
"""HWP Parser — extracts text from legacy HWP (OLE2 binary) files. stdlib only."""

import struct, zlib, json, sys, os, re

OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
ENDOFCHAIN = 0xFFFFFFFE
FREESECT = 0xFFFFFFFF
DIFSECT = 0xFFFFFFFC
FATSECT = 0xFFFFFFFD
HWPTAG_BEGIN = 0x0010
HWPTAG_PARA_TEXT = HWPTAG_BEGIN + 51

class OLE2Reader:
    def __init__(self, filepath):
        with open(filepath, "rb") as f:
            self.data = f.read()
        if self.data[:8] != OLE2_MAGIC:
            raise ValueError("Not a valid OLE2 file (wrong magic bytes)")
        self._parse_header()
        self._build_fat()
        self._build_minifat()
        self._read_directory()

    def _parse_header(self):
        h = self.data[:512]
        self.sector_size = 1 << struct.unpack_from("<H", h, 30)[0]
        self.mini_sector_size = 1 << struct.unpack_from("<H", h, 32)[0]
        self.total_fat_sectors = struct.unpack_from("<I", h, 44)[0]
        self.first_dir_sector = struct.unpack_from("<I", h, 48)[0]
        self.mini_stream_cutoff = struct.unpack_from("<I", h, 56)[0]
        self.first_minifat_sector = struct.unpack_from("<I", h, 60)[0]
        self.total_minifat_sectors = struct.unpack_from("<I", h, 64)[0]
        self.first_difat_sector = struct.unpack_from("<I", h, 68)[0]
        self.total_difat_sectors = struct.unpack_from("<I", h, 72)[0]
        self.difat = [struct.unpack_from("<I", h, 76 + i*4)[0] for i in range(109) if struct.unpack_from("<I", h, 76 + i*4)[0] < FATSECT]

    def _sector_offset(self, sid): return 512 + sid * self.sector_size
    def _read_sector(self, sid):
        o = self._sector_offset(sid)
        return self.data[o:o+self.sector_size]

    def _build_fat(self):
        if self.total_difat_sectors > 0:
            ds = self.first_difat_sector
            for _ in range(self.total_difat_sectors):
                if ds >= FATSECT: break
                sd = self._read_sector(ds)
                eps = self.sector_size // 4
                for j in range(eps - 1):
                    v = struct.unpack_from("<I", sd, j*4)[0]
                    if v < FATSECT: self.difat.append(v)
                ds = struct.unpack_from("<I", sd, (eps-1)*4)[0]
        self.fat = []
        for fsi in self.difat:
            sd = self._read_sector(fsi)
            for i in range(self.sector_size // 4):
                self.fat.append(struct.unpack_from("<I", sd, i*4)[0])

    def _build_minifat(self):
        self.minifat = []
        s = self.first_minifat_sector
        for _ in range(self.total_minifat_sectors):
            if s >= FATSECT: break
            sd = self._read_sector(s)
            for i in range(self.sector_size // 4):
                self.minifat.append(struct.unpack_from("<I", sd, i*4)[0])
            s = self.fat[s] if s < len(self.fat) else ENDOFCHAIN

    def _follow_chain(self, start, use_mini=False):
        chain, s, fat, visited = [], start, (self.minifat if use_mini else self.fat), set()
        while s < FATSECT and s not in visited:
            visited.add(s); chain.append(s)
            s = fat[s] if s < len(fat) else ENDOFCHAIN
        return chain

    def _read_directory(self):
        self.directory = []
        dd = b""
        for s in self._follow_chain(self.first_dir_sector): dd += self._read_sector(s)
        for i in range(len(dd) // 128):
            e = dd[i*128:(i+1)*128]
            nl = struct.unpack_from("<H", e, 64)[0]
            if nl == 0: continue
            self.directory.append({
                "name": e[:nl-2].decode("utf-16-le", errors="replace"),
                "type": struct.unpack_from("<B", e, 66)[0],
                "start": struct.unpack_from("<I", e, 116)[0],
                "size": struct.unpack_from("<I", e, 120)[0],
            })
        self.mini_stream = b""
        if self.directory:
            r = self.directory[0]
            if r["start"] < FATSECT and r["size"] > 0:
                for s in self._follow_chain(r["start"]): self.mini_stream += self._read_sector(s)

    def read_stream(self, name):
        for e in self.directory:
            if e["name"] == name: return self._read_entry(e)
        return None

    def read_stream_prefix(self, prefix):
        r = [(e["name"], self._read_entry(e)) for e in self.directory if e["name"].startswith(prefix) and self._read_entry(e) is not None]
        r.sort(key=lambda x: int(re.findall(r"(\d+)", x[0])[-1]) if re.findall(r"(\d+)", x[0]) else 0)
        return r

    def _read_entry(self, e):
        if e["size"] == 0: return b""
        if e["size"] < self.mini_stream_cutoff:
            d = b""
            for s in self._follow_chain(e["start"], True):
                o = s * self.mini_sector_size
                d += self.mini_stream[o:o+self.mini_sector_size]
            return d[:e["size"]]
        d = b""
        for s in self._follow_chain(e["start"]): d += self._read_sector(s)
        return d[:e["size"]]

    def list_streams(self): return [e["name"] for e in self.directory if e["type"] == 2]

def _is_compressed(fh):
    if fh and len(fh) >= 40:
        return bool(struct.unpack_from("<I", fh, 36)[0] & 0x01)
    return True

def _decompress(data, compressed=True):
    if not compressed: return data
    try: return zlib.decompress(data, -15)
    except:
        try: return zlib.decompress(data)
        except: return data

def _parse_records(data):
    records, pos = [], 0
    while pos + 4 <= len(data):
        h = struct.unpack_from("<I", data, pos)[0]
        tag, level, size = h & 0x3FF, (h >> 10) & 0x3FF, (h >> 20) & 0xFFF
        pos += 4
        if size == 0xFFF:
            if pos + 4 > len(data): break
            size = struct.unpack_from("<I", data, pos)[0]; pos += 4
        if pos + size > len(data): break
        records.append({"tag": tag, "data": data[pos:pos+size]}); pos += size
    return records

def _extract_text(payload):
    text, pos = [], 0
    while pos + 2 <= len(payload):
        code = struct.unpack_from("<H", payload, pos)[0]
        if code == 0: break
        elif code < 0x0020:
            if code in (0xA, 0xD): text.append("\n")
            elif code == 0x9: text.append("\t")
            pos += 16 if code in (1,2,3,11,12,14,15,16,17,18,21,22,23) else 2
        else:
            text.append(chr(code)); pos += 2
    return "".join(text).strip()

def parse_hwp(filepath):
    result = {"sections": [], "text": "", "tables": [], "metadata": {}}
    try: ole = OLE2Reader(filepath)
    except ValueError as e: result["error"] = str(e); return result
    except Exception as e: result["error"] = f"OLE2 read failed: {e}"; return result

    compressed = _is_compressed(ole.read_stream("FileHeader"))
    all_text, si = [], 0
    while True:
        sd = None
        for p in [f"Section{si}", f"BodyText/Section{si}"]:
            sd = ole.read_stream(p)
            if sd: break
        if sd is None:
            ss = ole.read_stream_prefix("Section")
            if si < len(ss): _, sd = ss[si]
        if sd is None: break
        raw = _decompress(sd, compressed)
        elements = []
        for rec in _parse_records(raw):
            if rec["tag"] == HWPTAG_PARA_TEXT:
                t = _extract_text(rec["data"])
                if t: elements.append({"type": "paragraph", "content": t}); all_text.append(t)
        result["sections"].append({"section": si, "elements": elements})
        si += 1
        if si > 100: break
    result["text"] = "\n".join(all_text)
    if not result["text"]:
        result["warning"] = "텍스트 추출 실패. 암호화 또는 미지원 HWP 버전일 수 있습니다."
    return result

def format_output(result):
    if "error" in result: return f"[오류] {result['error']}"
    lines = []
    if result.get("warning"): lines.extend([f"[경고] {result['warning']}", ""])
    for sec in result.get("sections", []):
        if len(result["sections"]) > 1: lines.append(f"=== 섹션 {sec.get('section','?')} ===")
        for e in sec.get("elements", []):
            if e["type"] == "paragraph": lines.append(e["content"])
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python parse_hwp.py <file.hwp> [--json]"); sys.exit(1)
    result = parse_hwp(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2) if "--json" in sys.argv else format_output(result))
