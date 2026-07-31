"""Pure detection functions over validated, supplied data."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .io import PROCESS_FIELDS

ENTRY_PREFIXES = {
    "c3": ("ret-at-entry", "high", "Function entry begins with RET."),
    "31c0c3": ("zero-return-stub", "high", "Function entry begins with XOR EAX,EAX; RET."),
    "e9": ("relative-jump-at-entry", "medium", "Function entry begins with a relative JMP."),
    "ff25": ("indirect-jump-at-entry", "medium", "Function entry begins with an indirect JMP."),
}


def _finding(
    finding_type: str,
    severity: str,
    title: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": finding_type,
        "severity": severity,
        "title": title,
        "evidence": evidence,
    }


def compare_inventories(
    baseline: dict[str, Any],
    observed: dict[str, Any],
    *,
    fields: Iterable[str] = PROCESS_FIELDS,
) -> list[dict[str, Any]]:
    baseline_by_pid = {item["pid"]: item for item in baseline["processes"]}
    observed_by_pid = {item["pid"]: item for item in observed["processes"]}
    findings: list[dict[str, Any]] = []

    for pid in sorted(baseline_by_pid.keys() - observed_by_pid.keys()):
        findings.append(
            _finding(
                "missing-from-observed-inventory",
                "high",
                f"PID {pid} is absent from the observed inventory",
                {
                    "pid": pid,
                    "baseline_source": baseline["source"],
                    "observed_source": observed["source"],
                    "baseline_record": baseline_by_pid[pid],
                },
            )
        )

    for pid in sorted(observed_by_pid.keys() - baseline_by_pid.keys()):
        findings.append(
            _finding(
                "missing-from-baseline-inventory",
                "medium",
                f"PID {pid} appears only in the observed inventory",
                {
                    "pid": pid,
                    "baseline_source": baseline["source"],
                    "observed_source": observed["source"],
                    "observed_record": observed_by_pid[pid],
                },
            )
        )

    for pid in sorted(baseline_by_pid.keys() & observed_by_pid.keys()):
        mismatches: dict[str, Any] = {}
        for field in fields:
            left = baseline_by_pid[pid].get(field)
            right = observed_by_pid[pid].get(field)
            if left is not None and right is not None and left != right:
                mismatches[field] = {"baseline": left, "observed": right}
        if mismatches:
            findings.append(
                _finding(
                    "inventory-field-mismatch",
                    "medium",
                    f"PID {pid} has inconsistent attributes",
                    {
                        "pid": pid,
                        "baseline_source": baseline["source"],
                        "observed_source": observed["source"],
                        "fields": mismatches,
                    },
                )
            )

    return findings


def inspect_entry_bytes(byte_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    source = byte_artifact["source"]
    for sample in byte_artifact["samples"]:
        observed = sample["observed_hex"]
        baseline = sample.get("baseline_hex")
        evidence = {
            "source": source,
            "component": sample["component"],
            "symbol": sample["symbol"],
            "observed_hex": observed,
        }
        if baseline is not None and observed != baseline:
            findings.append(
                _finding(
                    "entry-bytes-differ-from-baseline",
                    "high",
                    f"{sample['component']}!{sample['symbol']} differs from its supplied baseline",
                    {**evidence, "baseline_hex": baseline},
                )
            )

        for prefix, (finding_type, severity, message) in ENTRY_PREFIXES.items():
            if observed.startswith(prefix):
                findings.append(
                    _finding(
                        finding_type,
                        severity,
                        f"{sample['component']}!{sample['symbol']}: {message}",
                        {**evidence, "matched_prefix": prefix},
                    )
                )
                break

    return findings
