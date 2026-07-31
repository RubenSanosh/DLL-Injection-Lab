"""Stable report renderers for people and CI systems."""

from __future__ import annotations

import json
from typing import Any


def to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# DLL Injection Lab report",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Findings: **{report['summary']['finding_count']}**",
        "",
    ]
    if not report["findings"]:
        lines.append("No matching synthetic sequence or artifact discrepancy was found.")
        return "\n".join(lines) + "\n"

    lines.extend(["| Severity | Finding | Evidence |", "|---|---|---|"])
    for finding in report["findings"]:
        evidence = finding["evidence"]
        subject = (
            evidence.get("flow_id")
            or evidence.get("pid")
            or evidence.get("symbol")
            or evidence.get("source")
        )
        lines.append(f"| {finding['severity'].upper()} | {finding['title']} | `{subject}` |")
    lines.extend(
        [
            "",
            "> DLL Injection Lab analyzed synthetic or supplied data only. "
            "Findings are triage signals, "
            "not proof of compromise.",
        ]
    )
    return "\n".join(lines) + "\n"


def to_sarif(report: dict[str, Any]) -> str:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    level_map = {"high": "error", "medium": "warning", "low": "note"}
    for finding in report["findings"]:
        rule_id = finding["type"]
        rules.setdefault(
            rule_id,
            {
                "id": rule_id,
                "shortDescription": {"text": finding["title"]},
                "helpUri": (
                    "https://github.com/bsmensah-ctrl/"
                    "DLL-Injection-Lab#the-chain-your-detector-must-catch"
                ),
            },
        )
        evidence = finding["evidence"]
        source = evidence.get("source") or evidence.get("observed_source") or "supplied-artifact"
        results.append(
            {
                "ruleId": rule_id,
                "level": level_map[finding["severity"]],
                "message": {"text": finding["title"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f"crossview-input://{source}"}
                        }
                    }
                ],
                "properties": {"evidence": evidence, "offlineArtifactOnly": True},
            }
        )

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "DLL Injection Lab",
                        "version": report["tool"]["version"],
                        "informationUri": "https://github.com/bsmensah-ctrl/DLL-Injection-Lab",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, indent=2, sort_keys=True) + "\n"
