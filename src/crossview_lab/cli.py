"""Command-line interface for deterministic offline analysis."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .analyzer import analyze
from .errors import InputError
from .formatters import to_json, to_markdown, to_sarif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crossview-lab",
        description=(
            "Compare supplied process-inventory exports and inspect supplied entry-byte fixtures. "
            "No live host collection is performed."
        ),
    )
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline inventory JSON")
    parser.add_argument("--observed", type=Path, required=True, help="Observed inventory JSON")
    parser.add_argument("--entry-bytes", type=Path, help="Optional supplied entry-byte JSON")
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "sarif"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--output", type=Path, help="Write to a file instead of stdout")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit 1 when findings exist; useful in CI",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = analyze(args.baseline, args.observed, args.entry_bytes)
    except InputError as exc:
        parser.error(str(exc))

    renderers = {"json": to_json, "markdown": to_markdown, "sarif": to_sarif}
    rendered = renderers[args.format](report)
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            parser.error(f"cannot write {args.output}: {exc}")

    return 1 if args.fail_on_findings and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
