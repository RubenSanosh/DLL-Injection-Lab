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

DLL_INJECTION_SEQUENCE = (
    "cross_process_handle_open",
    "remote_memory_allocation",
    "remote_memory_write",
    "remote_thread_start",
    "image_load",
)


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


def detect_dll_injection_sequence(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect the complete synthetic event chain within each correlation flow."""
    flows: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        flows.setdefault(event["flow_id"], []).append(event)

    findings: list[dict[str, Any]] = []
    for flow_id, flow_events in sorted(flows.items()):
        candidates: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
        for event in flow_events:
            identity = (event["actor_pid"], event["target_pid"], event["module"])
            candidates.setdefault(identity, []).append(event)

        for (actor_pid, target_pid, module), candidate_events in sorted(candidates.items()):
            if actor_pid == target_pid:
                continue

            ordered = sorted(candidate_events, key=lambda event: event["tick"])
            actions = [event["action"] for event in ordered]
            positions: list[int] = []
            cursor = 0
            for required_action in DLL_INJECTION_SEQUENCE:
                try:
                    position = actions.index(required_action, cursor)
                except ValueError:
                    break
                positions.append(position)
                cursor = position + 1

            if len(positions) != len(DLL_INJECTION_SEQUENCE):
                continue

            matched = [ordered[position] for position in positions]
            findings.append(
                _finding(
                    "synthetic-dll-injection-sequence",
                    "high",
                    f"Synthetic DLL-injection sequence detected in flow {flow_id}",
                    {
                        "scenario": matched[0]["scenario"],
                        "flow_id": flow_id,
                        "actor_pid": actor_pid,
                        "target_pid": target_pid,
                        "module": module,
                        "matched_actions": list(DLL_INJECTION_SEQUENCE),
                        "matched_ticks": [event["tick"] for event in matched],
                        "first_tick": matched[0]["tick"],
                        "last_tick": matched[-1]["tick"],
                        "synthetic": True,
                        "attack_technique": "T1055.001",
                    },
                )
            )
    return findings
