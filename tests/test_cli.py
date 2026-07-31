import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def command(*extra):
    return [
        sys.executable,
        "-m",
        "crossview_lab",
        "artifacts",
        "--baseline",
        str(FIXTURES / "inventory_baseline.json"),
        "--observed",
        str(FIXTURES / "inventory_observed.json"),
        "--format",
        "json",
        *extra,
    ]


def test_cli_outputs_json_without_failing_by_default():
    result = subprocess.run(command(), check=True, capture_output=True, text=True)

    assert json.loads(result.stdout)["summary"]["finding_count"] == 2


def test_cli_can_fail_ci_when_findings_exist():
    result = subprocess.run(command("--fail-on-findings"), capture_output=True, text=True)

    assert result.returncode == 1
    assert json.loads(result.stdout)["summary"]["finding_count"] == 2


def test_cli_writes_sarif_file(tmp_path):
    output = tmp_path / "report.sarif"

    args = command()
    format_index = args.index("json")
    args[format_index] = "sarif"
    subprocess.run([*args, "--output", str(output)], check=True)

    assert json.loads(output.read_text(encoding="utf-8"))["version"] == "2.1.0"


def test_cli_demo_detects_the_built_in_sequence():
    result = subprocess.run(
        [sys.executable, "-m", "crossview_lab", "demo", "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    )

    report = json.loads(result.stdout)
    assert report["mode"] == "synthetic-event-only"
    assert report["summary"]["event_count"] == 5
    assert report["findings"][0]["type"] == "synthetic-dll-injection-sequence"


def test_cli_simulate_can_feed_cli_detect(tmp_path):
    events = tmp_path / "events.jsonl"
    subprocess.run(
        [sys.executable, "-m", "crossview_lab", "simulate", "--output", str(events)],
        check=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "crossview_lab",
            "detect",
            "--events",
            str(events),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["summary"]["finding_count"] == 1
