"""Strict readers for user-supplied, offline JSON artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import InputError

PROCESS_FIELDS = ("name", "ppid", "path", "user", "command_line")
_HEX_SEPARATOR = re.compile(r"[\s:_-]+")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc.msg} at line {exc.lineno}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{path} must contain a JSON object")
    return value


def load_inventory(path: Path) -> dict[str, Any]:
    value = load_json(path)
    source = value.get("source")
    processes = value.get("processes")
    if not isinstance(source, str) or not source.strip():
        raise InputError(f"{path}: 'source' must be a non-empty string")
    if not isinstance(processes, list):
        raise InputError(f"{path}: 'processes' must be an array")

    seen: set[int] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(processes):
        if not isinstance(item, dict):
            raise InputError(f"{path}: processes[{index}] must be an object")
        pid = item.get("pid")
        if isinstance(pid, bool) or not isinstance(pid, int) or pid < 0:
            raise InputError(f"{path}: processes[{index}].pid must be a non-negative integer")
        if pid in seen:
            raise InputError(f"{path}: duplicate PID {pid}")
        seen.add(pid)
        normalized.append(dict(item))

    return {"source": source.strip(), "processes": normalized}


def normalize_hex(value: str) -> str:
    if not isinstance(value, str):
        raise InputError("entry bytes must be a string")
    without_prefixes = re.sub(r"0[xX]", "", value)
    normalized = _HEX_SEPARATOR.sub("", without_prefixes).lower()
    if not normalized:
        raise InputError("entry bytes cannot be empty")
    if re.fullmatch(r"[0-9a-f]+", normalized) is None:
        raise InputError(f"invalid hexadecimal byte string: {value!r}")
    if len(normalized) % 2:
        raise InputError(f"hexadecimal byte string has an odd number of digits: {value!r}")
    return normalized


def load_byte_samples(path: Path) -> dict[str, Any]:
    value = load_json(path)
    source = value.get("source")
    samples = value.get("samples")
    if not isinstance(source, str) or not source.strip():
        raise InputError(f"{path}: 'source' must be a non-empty string")
    if not isinstance(samples, list):
        raise InputError(f"{path}: 'samples' must be an array")

    normalized: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise InputError(f"{path}: samples[{index}] must be an object")
        component = sample.get("component")
        symbol = sample.get("symbol")
        if not isinstance(component, str) or not component.strip():
            raise InputError(f"{path}: samples[{index}].component must be a string")
        if not isinstance(symbol, str) or not symbol.strip():
            raise InputError(f"{path}: samples[{index}].symbol must be a string")
        observed = normalize_hex(sample.get("observed_hex"))
        record = {
            "component": component.strip().lower(),
            "symbol": symbol.strip(),
            "observed_hex": observed,
        }
        if "baseline_hex" in sample:
            record["baseline_hex"] = normalize_hex(sample["baseline_hex"])
        normalized.append(record)

    return {"source": source.strip(), "samples": normalized}
