"""Command-line interface for deterministic offline analysis."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .analyzer import analyze, analyze_events
from .errors import InputError
from .formatters import to_json, to_markdown, to_sarif
from .simulator import (
    SCENARIOS,
    STREAM_VARIANTS,
    events_to_jsonl,
    load_event_stream,
    simulate_scenario,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dll-injection-lab",
        description=(
            "Simulate and detect DLL-injection telemetry without touching a live process."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="Run the built-in synthetic detection demo")
    demo.add_argument("--scenario", choices=SCENARIOS, default="classic")
    _add_variant_argument(demo)
    _add_report_arguments(demo)

    simulate = subparsers.add_parser("simulate", help="Emit a synthetic JSONL event stream")
    simulate.add_argument("--scenario", choices=SCENARIOS, default="classic")
    _add_variant_argument(simulate)
    simulate.add_argument("--output", type=Path, help="Write JSONL to a file instead of stdout")

    detect = subparsers.add_parser("detect", help="Detect a supplied synthetic JSONL event stream")
    detect.add_argument("--events", type=Path, required=True, help="Synthetic event-stream JSONL")
    _add_report_arguments(detect)

    artifacts = subparsers.add_parser(
        "artifacts", help="Analyze supplied inventory and entry-byte artifacts"
    )
    artifacts.add_argument("--baseline", type=Path, required=True, help="Baseline inventory JSON")
    artifacts.add_argument("--observed", type=Path, required=True, help="Observed inventory JSON")
    artifacts.add_argument("--entry-bytes", type=Path, help="Optional supplied entry-byte JSON")
    _add_report_arguments(artifacts)
    return parser


def _add_report_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "sarif"),
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument("--output", type=Path, help="Write to a file instead of stdout")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit 1 when findings exist; useful in CI",
    )


def _add_variant_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--variant",
        choices=STREAM_VARIANTS,
        default="complete",
        help="Model complete, missing, delayed, or duplicate event delivery",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments and arguments[0].startswith("--"):
        arguments.insert(0, "artifacts")
    args = parser.parse_args(arguments)

    try:
        if args.command == "simulate":
            rendered = events_to_jsonl(simulate_scenario(args.scenario, variant=args.variant))
            return _write_output(rendered, args.output, parser)
        if args.command == "demo":
            events = simulate_scenario(args.scenario, variant=args.variant)
            report = analyze_events(events, source=f"built-in:{args.scenario}:{args.variant}")
        elif args.command == "detect":
            report = analyze_events(load_event_stream(args.events), source=str(args.events))
        else:
            report = analyze(args.baseline, args.observed, args.entry_bytes)
    except InputError as exc:
        parser.error(str(exc))

    renderers = {"json": to_json, "markdown": to_markdown, "sarif": to_sarif}
    rendered = renderers[args.format](report)
    _write_output(rendered, args.output, parser)

    return 1 if args.fail_on_findings and report["findings"] else 0


def _write_output(rendered: str, output: Path | None, parser: argparse.ArgumentParser) -> int:
    if output is None:
        sys.stdout.write(rendered)
    else:
        try:
            output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            parser.error(f"cannot write {output}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
