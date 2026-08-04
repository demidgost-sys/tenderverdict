#!/usr/bin/env python3
"""Minimal offline CLI embedded in the TenderVerdict Next Gen macOS app."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tenderverdict.models import (
    MAX_NOTICES_FILE_BYTES,
    MAX_WORKSPACE_FILE_BYTES,
    Notice,
    SchemaValidationError,
    notice_collection_from_file_bytes,
    parse_review_point,
    portfolio_workspace_from_json_bytes,
    read_bounded_file_bytes,
)
from tenderverdict.workflow import dump_json, qualify_portfolio_files, render_portfolio_run

_DEFAULT_PREVIEW_LIMIT = 5
_MAX_PREVIEW_LIMIT = 20
_CANONICAL_NOTICE_FIELDS = (
    "publication_number",
    "lot_id",
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "deadline_at",
    "publication_date",
    "source_url",
    "metadata_warnings",
)
_MISSING_NOTICE_FIELDS = (
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "source_url",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="TenderVerdictCore")
    subparsers = parser.add_subparsers(dest="command", required=True)
    portfolio = subparsers.add_parser(
        "portfolio",
        help="run the bounded local Portfolio Workspace workflow",
    )
    portfolio.add_argument("--workspace", required=True, type=Path)
    portfolio.add_argument("--notices", required=True, type=Path)
    portfolio.add_argument("--as-of", required=True, metavar="DATE_OR_RFC3339")
    portfolio.set_defaults(handler=_run_portfolio)

    normalize_workspace = subparsers.add_parser(
        "normalize-workspace",
        help="validate and normalize one local Portfolio Workspace",
    )
    normalize_workspace.add_argument("--workspace", required=True, type=Path)
    normalize_workspace.set_defaults(handler=_run_normalize_workspace)

    inspect_notices = subparsers.add_parser(
        "inspect-notices",
        help="validate local notices and emit a bounded normalized preview",
    )
    inspect_notices.add_argument("--notices", required=True, type=Path)
    inspect_notices.add_argument(
        "--limit",
        type=_preview_limit,
        default=_DEFAULT_PREVIEW_LIMIT,
        help=f"preview between 1 and {_MAX_PREVIEW_LIMIT} notices (default: 5)",
    )
    inspect_notices.set_defaults(handler=_run_inspect_notices)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (SchemaValidationError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run_portfolio(args: argparse.Namespace) -> int:
    as_of = parse_review_point(args.as_of, "--as-of")
    run = qualify_portfolio_files(args.workspace, args.notices, as_of=as_of)
    sys.stdout.write(render_portfolio_run(run))
    return 0


def _run_normalize_workspace(args: argparse.Namespace) -> int:
    payload = read_bounded_file_bytes(args.workspace, MAX_WORKSPACE_FILE_BYTES, "workspace")
    workspace = portfolio_workspace_from_json_bytes(payload, args.workspace)
    sys.stdout.write(dump_json(workspace.to_dict()))
    return 0


def _run_inspect_notices(args: argparse.Namespace) -> int:
    payload = read_bounded_file_bytes(args.notices, MAX_NOTICES_FILE_BYTES, "notices")
    collection = notice_collection_from_file_bytes(payload, args.notices)
    preview = [_notice_metadata(notice) for notice in collection.notices[: args.limit]]
    result = {
        "schema_version": 1,
        "kind": "notice_import_preview",
        "source_kind": collection.source_kind,
        "notice_count": len(collection.notices),
        "canonical_fields": list(_CANONICAL_NOTICE_FIELDS),
        "preview": preview,
        "missing_field_counts": {
            field: sum(_is_missing(notice, field) for notice in collection.notices)
            for field in _MISSING_NOTICE_FIELDS
        },
    }
    sys.stdout.write(dump_json(result))
    return 0


def _preview_limit(value: str) -> int:
    try:
        limit = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 through 20") from exc
    if not 1 <= limit <= _MAX_PREVIEW_LIMIT:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 through 20")
    return limit


def _notice_metadata(notice: Notice) -> dict[str, object]:
    return {
        "publication_number": notice.publication_number,
        "lot_id": notice.lot_id,
        "notice_type": notice.notice_type,
        "title": notice.title,
        "buyer": notice.buyer,
        "cpv_codes": list(notice.cpv_codes),
        "countries": list(notice.countries),
        "deadline": notice.deadline.isoformat() if notice.deadline else None,
        "deadline_at": notice.deadline_at.isoformat() if notice.deadline_at else None,
        "publication_date": notice.publication_date.isoformat()
        if notice.publication_date
        else None,
        "source_url": notice.source_url,
        "metadata_warnings": list(notice.metadata_warnings),
    }


def _is_missing(notice: Notice, field: str) -> bool:
    if field == "deadline":
        return notice.deadline is None and notice.deadline_at is None
    value = getattr(notice, field)
    return value is None or value == ()


if __name__ == "__main__":
    raise SystemExit(main())
