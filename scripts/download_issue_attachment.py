#!/usr/bin/env python3
"""Download the first matching GitHub issue attachment URL from issue text."""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)>\"]+")


def candidates(text: str, extension: str) -> list[tuple[str, str]]:
    ext = extension.lower().lstrip(".")
    markdown_links = MARKDOWN_LINK_RE.findall(text)
    matches: list[tuple[str, str]] = []
    for label, url in markdown_links:
        if label.lower().split("?")[0].endswith(f".{ext}") or url.lower().split("?")[0].endswith(f".{ext}"):
            matches.append((label, url))
    if markdown_links:
        return matches

    for url in URL_RE.findall(text):
        if url.lower().split("?")[0].endswith(f".{ext}") or "github.com/user-attachments/" in url:
            matches.append((Path(url).name or f"input.{ext}", url))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--extension", required=True, help="Expected extension, for example pdf or xlsx")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    text = Path(args.body_file).read_text(encoding="utf-8")
    found = candidates(text, args.extension)
    if not found:
        print(f"No .{args.extension.lstrip('.')} attachment URL found in issue body.", file=sys.stderr)
        return 1

    label, url = found[0]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {label}: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "yameskills-actions"})
    with urllib.request.urlopen(request) as response:
        output.write_bytes(response.read())
    print(f"Saved {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
