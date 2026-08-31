"""Command-line interface for TenderVerdict."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .models import (
    SchemaValidationError,
    parse_review_point,
)
from .output import write_text_atomically
from .ted import TedApiError, build_ted_snapshot, fetch_notices
from .workflow import (
    demo_run,
    dump_json,
    qualify_files,
    qualify_portfolio_files,
    render_portfolio_run,
    render_run,
)


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
        "qualify", help="qualify normalized notice metadata from local CSV or JSON files"
    )
    qualify_parser.add_argument("--profile", required=True, type=Path)
    qualify_parser.add_argument("--notices", required=True, type=Path)
    qualify_parser.add_argument(
        "--as-of",
        required=True,
        metavar="DATE_OR_RFC3339",
        help="explicit review date or timezone-aware instant; system time is never used",
    )
    _add_format_arguments(qualify_parser)
    qualify_parser.set_defaults(handler=_run_qualify)

    portfolio_parser = subparsers.add_parser(
        "portfolio",
        help="qualify one notice set independently for up to five named profiles",
    )
    portfolio_parser.add_argument("--workspace", required=True, type=Path)
    portfolio_parser.add_argument("--notices", required=True, type=Path)
    portfolio_parser.add_argument(
        "--as-of",
        required=True,
        metavar="DATE_OR_RFC3339",
        help="explicit review date or timezone-aware instant; system time is never used",
    )
    portfolio_parser.add_argument(
        "--output",
        type=Path,
        help="write JSON atomically to this file; omit to print to stdout",
    )
    portfolio_parser.set_defaults(handler=_run_portfolio)

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
    as_of = parse_review_point(args.as_of, "--as-of")
    run = qualify_files(args.profile, args.notices, as_of=as_of)
    _emit(render_run(run, args.format), args.output)
    return 0


def _run_portfolio(args: argparse.Namespace) -> int:
    as_of = parse_review_point(args.as_of, "--as-of")
    run = qualify_portfolio_files(args.workspace, args.notices, as_of=as_of)
    _emit(render_portfolio_run(run), args.output)
    return 0


def _run_fetch_ted(args: argparse.Namespace) -> int:
    notices = fetch_notices(args.query, max_notices=args.max_notices)
    _emit(dump_json(build_ted_snapshot(args.query, notices)), args.output)
    return 0


def _run_desktop(_args: argparse.Namespace) -> int:
    from .desktop import main as desktop_main

    return desktop_main([])


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content)
        return
    write_text_atomically(output, content)
