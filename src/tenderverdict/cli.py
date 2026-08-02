"""Command-line interface for TenderVerdict."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from .demo_data import DEMO_AS_OF, demo_notices, demo_profile
from .models import (
    SchemaValidationError,
    load_notices,
    load_profile,
    notices_from_data,
    parse_iso_date,
    profile_from_dict,
)
from .qualification import qualify_notices
from .report import render_html, render_markdown, report_as_dict
from .ted import TedApiError, fetch_notices


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
    profile = profile_from_dict(demo_profile())
    notices = notices_from_data(demo_notices())
    as_of = parse_iso_date(DEMO_AS_OF, "demo.as_of")
    results = qualify_notices(profile, notices, as_of=as_of)
    _emit(_render(args.format, profile, results, as_of), args.output)
    return 0


def _run_qualify(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    notices = load_notices(args.notices)
    as_of = parse_iso_date(args.as_of, "--as-of")
    results = qualify_notices(profile, notices, as_of=as_of)
    _emit(_render(args.format, profile, results, as_of), args.output)
    return 0


def _run_fetch_ted(args: argparse.Namespace) -> int:
    notices = fetch_notices(args.query, max_notices=args.max_notices)
    _emit(_dump_json(notices), args.output)
    return 0


def _render(format_name: str, profile: object, results: object, as_of: object) -> str:
    if format_name == "markdown":
        return render_markdown(profile, results, as_of=as_of)
    if format_name == "html":
        return render_html(profile, results, as_of=as_of)
    if format_name == "json":
        return _dump_json(report_as_dict(profile, results, as_of=as_of))
    raise ValueError(f"unsupported format: {format_name}")


def _dump_json(payload: object) -> str:
    """Serialize untrusted metadata without raw terminal or bidi controls."""

    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content)
        return
    _atomic_write_text(output, content)


def _atomic_write_text(destination: Path, content: str) -> None:
    destination = destination.expanduser()
    parent = destination.parent
    if not parent.is_dir():
        raise OSError(f"output directory does not exist: {parent}")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except BaseException:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise
