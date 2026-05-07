from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


def load_structured_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {path}")

    suffix = path.suffix.lower()
    with path.open("r", encoding="utf-8") as handle:
        if suffix in {".yaml", ".yml"}:
            content = handle.read()
            data = yaml.safe_load(content) if yaml else _load_simple_yaml(content)
        elif suffix == ".json":
            data = json.load(handle)
        else:
            raise ValueError("입력 파일은 .yaml, .yml, .json 중 하나여야 합니다.")

    if not isinstance(data, dict):
        raise ValueError("입력 파일의 최상위 구조는 객체여야 합니다.")
    return data


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    normalized = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    normalized = re.sub(r"\s+", "_", normalized)
    return normalized or "sample"


def _load_simple_yaml(content: str) -> dict[str, Any]:
    """Small YAML subset parser for the checked-in sample files.

    PyYAML remains the supported parser. This fallback keeps the CLI usable in
    a freshly provisioned Codex runtime before dependencies are installed.
    """
    result: dict[str, Any] = {}
    current_list_name: str | None = None
    current_item: dict[str, Any] | None = None

    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            current_list_name = line[:-1]
            result[current_list_name] = []
            current_item = None
            continue

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = _parse_scalar(value.strip())
            current_list_name = None
            current_item = None
            continue

        if current_list_name and line.startswith("- "):
            current_item = {}
            result[current_list_name].append(current_item)
            remainder = line[2:].strip()
            if remainder:
                key, value = remainder.split(":", 1)
                current_item[key.strip()] = _parse_scalar(value.strip())
            continue

        if current_item is not None and ":" in line:
            key, value = line.split(":", 1)
            current_item[key.strip()] = _parse_scalar(value.strip())
            continue

        raise ValueError("PyYAML이 설치되지 않았고 fallback YAML 파서가 처리할 수 없는 구조입니다.")

    return result


def _parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value
