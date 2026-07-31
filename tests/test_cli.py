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
        "--baseline",
        str(FIXTURES / "inventory_baseline.json"),
        "--observed",
        str(FIXTURES / "inventory_observed.json"),
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

    subprocess.run(command("--format", "sarif", "--output", str(output)), check=True)

    assert json.loads(output.read_text(encoding="utf-8"))["version"] == "2.1.0"
