"""Report assembly for the CrossViewLab public API."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .detectors import compare_inventories, inspect_entry_bytes
from .io import load_byte_samples, load_inventory


def analyze(
    baseline_path: Path,
    observed_path: Path,
    byte_samples_path: Path | None = None,
) -> dict[str, Any]:
    baseline = load_inventory(baseline_path)
    observed = load_inventory(observed_path)
    findings = compare_inventories(baseline, observed)
    inputs: dict[str, Any] = {
        "baseline_inventory": str(baseline_path),
        "observed_inventory": str(observed_path),
    }

    if byte_samples_path is not None:
        byte_artifact = load_byte_samples(byte_samples_path)
        findings.extend(inspect_entry_bytes(byte_artifact))
        inputs["entry_bytes"] = str(byte_samples_path)

    severity_counts = Counter(finding["severity"] for finding in findings)
    type_counts = Counter(finding["type"] for finding in findings)
    return {
        "schema_version": "1.0.0",
        "tool": {"name": "CrossViewLab", "version": "0.1.0"},
        "mode": "offline-artifact-only",
        "inputs": inputs,
        "summary": {
            "finding_count": len(findings),
            "by_severity": dict(sorted(severity_counts.items())),
            "by_type": dict(sorted(type_counts.items())),
        },
        "findings": findings,
    }
