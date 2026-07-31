import json
from pathlib import Path

import pytest
from jsonschema import validate

from crossview_lab.analyzer import analyze_events
from crossview_lab.detectors import DLL_INJECTION_SEQUENCE, detect_dll_injection_sequence
from crossview_lab.errors import InputError
from crossview_lab.simulator import load_event_stream, simulate_scenario


def test_classic_scenario_is_deterministic_and_synthetic():
    first = simulate_scenario("classic")
    second = simulate_scenario("classic")

    assert first == second
    assert [event["action"] for event in first] == list(DLL_INJECTION_SEQUENCE)
    assert all(event["synthetic"] is True for event in first)
    assert all(event["actor_pid"] != event["target_pid"] for event in first)


def test_classic_scenario_produces_one_correlated_finding():
    findings = detect_dll_injection_sequence(simulate_scenario("classic"))

    assert len(findings) == 1
    assert findings[0]["type"] == "synthetic-dll-injection-sequence"
    assert findings[0]["evidence"]["attack_technique"] == "T1055.001"
    assert findings[0]["evidence"]["matched_actions"] == list(DLL_INJECTION_SEQUENCE)


def test_cooperative_same_process_load_is_a_clean_control():
    events = simulate_scenario("cooperative")

    assert detect_dll_injection_sequence(events) == []
    assert all(event["actor_pid"] == event["target_pid"] for event in events)


def test_incomplete_sequence_does_not_produce_a_finding():
    events = simulate_scenario("classic")
    events = [event for event in events if event["action"] != "remote_thread_start"]

    assert detect_dll_injection_sequence(events) == []


def test_reordered_sequence_does_not_produce_a_finding():
    events = simulate_scenario("classic")
    events[2]["tick"], events[3]["tick"] = events[3]["tick"], events[2]["tick"]

    assert detect_dll_injection_sequence(events) == []


def test_unrelated_repeated_event_does_not_hide_a_valid_sequence():
    events = simulate_scenario("classic")
    unrelated_write = events[2].copy()
    unrelated_write["actor_pid"] = 9999
    unrelated_write["tick"] = 3
    for event in events[2:]:
        event["tick"] += 1
    events.append(unrelated_write)

    findings = detect_dll_injection_sequence(events)

    assert len(findings) == 1
    assert findings[0]["evidence"]["actor_pid"] == 4100
    assert findings[0]["evidence"]["matched_ticks"] == [1, 2, 4, 5, 6]


def test_sequence_requires_consistent_actor_target_and_module():
    changed_target = simulate_scenario("classic")
    changed_target[2]["target_pid"] = 4201
    changed_module = simulate_scenario("classic")
    changed_module[-1]["module"] = "synthetic://lab/different-module.dll"

    assert detect_dll_injection_sequence(changed_target) == []
    assert detect_dll_injection_sequence(changed_module) == []


def test_event_report_is_schema_valid():
    report = analyze_events(simulate_scenario("classic"), source="built-in:classic")
    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "report.schema.json").read_text(
            encoding="utf-8"
        )
    )

    validate(report, schema)
    assert report["tool"]["name"] == "DLL Injection Lab"


def test_event_loader_rejects_stream_without_synthetic_declaration(tmp_path):
    path = tmp_path / "events.jsonl"
    event = simulate_scenario("classic")[0]
    event["synthetic"] = False
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")

    with pytest.raises(InputError, match="synthetic=true"):
        load_event_stream(path)


@pytest.mark.parametrize(
    ("scenario", "fixture_name"),
    [("classic", "dll_injection_classic.jsonl"), ("cooperative", "cooperative_load.jsonl")],
)
def test_public_event_fixtures_match_the_built_in_scenarios(scenario, fixture_name):
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / fixture_name

    assert load_event_stream(fixture) == simulate_scenario(scenario)
