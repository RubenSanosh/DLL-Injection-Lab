"""Deterministic, in-memory DLL-injection telemetry simulation.

The simulator emits event dictionaries only. It does not import or call any
platform API and never interacts with a live process.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .errors import InputError

SCENARIOS = ("classic", "cooperative")

_CLASSIC_ACTIONS = (
    ("cross_process_handle_open", "A synthetic process handle is requested."),
    ("remote_memory_allocation", "A synthetic remote memory region is reserved."),
    ("remote_memory_write", "A fictional library path is staged in the region."),
    ("remote_thread_start", "A synthetic remote execution event is emitted."),
    ("image_load", "The fictional target records a new module image."),
)

_COOPERATIVE_ACTIONS = (
    ("user_approval", "The fictional user approves a local plug-in load."),
    ("self_module_load_requested", "The host requests a module in its own process."),
    ("image_load", "The fictional host records the approved plug-in image."),
)


def simulate_scenario(name: str) -> list[dict[str, Any]]:
    """Return a deterministic synthetic event stream for an educational scenario."""
    if name not in SCENARIOS:
        raise InputError(f"unknown scenario {name!r}; expected one of {', '.join(SCENARIOS)}")

    if name == "classic":
        actions = _CLASSIC_ACTIONS
        actor_pid, target_pid = 4100, 4200
        module = "synthetic://lab/telemetry-demo.dll"
        flow_id = "classic-dll-injection-001"
    else:
        actions = _COOPERATIVE_ACTIONS
        actor_pid = target_pid = 4300
        module = "synthetic://lab/approved-plugin.dll"
        flow_id = "cooperative-plugin-001"

    return [
        {
            "schema_version": "1.0.0",
            "scenario": name,
            "flow_id": flow_id,
            "tick": tick,
            "actor_pid": actor_pid,
            "target_pid": target_pid,
            "action": action,
            "module": module,
            "description": description,
            "synthetic": True,
        }
        for tick, (action, description) in enumerate(actions, start=1)
    ]


def events_to_jsonl(events: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(event, sort_keys=True) + "\n" for event in events)


def load_event_stream(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc

    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"invalid JSONL in {path} at line {line_number}: {exc.msg}") from exc
        if not isinstance(event, dict):
            raise InputError(f"{path}:{line_number} must contain a JSON object")
        _validate_event(event, path, line_number)
        events.append(event)

    if not events:
        raise InputError(f"{path} contains no events")
    return events


def _validate_event(event: dict[str, Any], path: Path, line_number: int) -> None:
    required_strings = ("scenario", "flow_id", "action", "module", "description")
    for field in required_strings:
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise InputError(f"{path}:{line_number} field {field!r} must be a non-empty string")
    for field in ("tick", "actor_pid", "target_pid"):
        value = event.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise InputError(f"{path}:{line_number} field {field!r} must be a non-negative integer")
    if event.get("synthetic") is not True:
        raise InputError(f"{path}:{line_number} must declare synthetic=true")
