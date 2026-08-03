"""Command-line interface for TenderVerdict."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .models import (
    SchemaValidationError,
    parse_iso_date,
)
from .output import write_text_atomically
from .ted import TedApiError, fetch_notices
from .workflow import demo_run, dump_json, qualify_files, render_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tenderverdict",
        description=(
            "Deterministic, local-first pre-qualification of public-procurement notice metadata."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser(
        "demo", help="render the bundled synthetic example without network access"
    )
    _add_format_arguments(demo_parser)
    demo_parser.set_defaults(handler=_run_demo)

    qualify_parser = subparsers.add_parser(
        "qualify", help="qualify normalized notice metadata from local JSON files"
    )
    qualify_parser.add_argument("--profile", required=True, type=Path)
    qualify_parser.add_argument("--notices", required=True, type=Path)
    qualify_parser.add_argument(
        "--as-of",
        required=True,
        metavar="YYYY-MM-DD",
        help="explicit review date; system time is never used",
    )
    _add_format_arguments(qualify_parser)
    qualify_parser.set_defaults(handler=_run_qualify)

    fetch_parser = subparsers.add_parser(
        "fetch-ted", help="explicitly fetch bounded metadata from the public TED Search API"
    )
    fetch_parser.add_argument("--query", required=True, help="TED expert query")
    fetch_parser.add_argument("--max-notices", required=True, type=int)
    fetch_parser.add_argument("--output", required=True, type=Path)
    fetch_parser.set_defaults(handler=_run_fetch_ted)

    desktop_parser = subparsers.add_parser(
        "desktop", help="launch the local desktop preview (requires a Python build with Tk)"
    )
    desktop_parser.set_defaults(handler=_run_desktop)

    return parser


def _add_format_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("markdown", "html", "json"),
        default="markdown",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write atomically to this file; omit to print to stdout",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (SchemaValidationError, TedApiError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run_demo(args: argparse.Namespace) -> int:
    run = demo_run()
    _emit(render_run(run, args.format), args.output)
    return 0


def _run_qualify(args: argparse.Namespace) -> int:
    as_of = parse_iso_date(args.as_of, "--as-of")
    run = qualify_files(args.profile, args.notices, as_of=as_of)
    _emit(render_run(run, args.format), args.output)
    return 0


def _run_fetch_ted(args: argparse.Namespace) -> int:
    notices = fetch_notices(args.query, max_notices=args.max_notices)
    _emit(dump_json(notices), args.output)
    return 0


def _run_desktop(_args: argparse.Namespace) -> int:
    from .desktop import main as desktop_main

    return desktop_main([])


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content)
        return
    write_text_atomically(output, content)
