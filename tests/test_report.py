import json
from pathlib import Path

from jsonschema import validate

from crossview_lab.analyzer import analyze
from crossview_lab.formatters import to_markdown, to_sarif

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def test_demo_report_is_schema_valid_and_deterministic():
    report = analyze(
        FIXTURES / "inventory_baseline.json",
        FIXTURES / "inventory_observed.json",
        FIXTURES / "entry_bytes.json",
    )
    schema = json.loads((ROOT / "schemas" / "report.schema.json").read_text(encoding="utf-8"))

    validate(report, schema)
    assert report["mode"] == "offline-artifact-only"
    assert report["summary"] == {
        "finding_count": 6,
        "by_severity": {"high": 4, "medium": 2},
        "by_type": {
            "entry-bytes-differ-from-baseline": 2,
            "missing-from-baseline-inventory": 1,
            "missing-from-observed-inventory": 1,
            "relative-jump-at-entry": 1,
            "ret-at-entry": 1,
        },
    }


def test_markdown_renderer_contains_triage_disclaimer():
    report = analyze(FIXTURES / "inventory_baseline.json", FIXTURES / "inventory_observed.json")

    rendered = to_markdown(report)

    assert "# CrossViewLab report" in rendered
    assert "triage signals, not proof of compromise" in rendered


def test_sarif_renderer_emits_results_and_rules():
    report = analyze(FIXTURES / "inventory_baseline.json", FIXTURES / "inventory_observed.json")

    sarif = json.loads(to_sarif(report))

    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"][0]["results"]) == 2
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == 2
