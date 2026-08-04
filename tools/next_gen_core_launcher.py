#!/usr/bin/env python3
"""Minimal offline CLI embedded in the TenderVerdict Next Gen macOS app."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tenderverdict.models import SchemaValidationError, parse_review_point
from tenderverdict.workflow import qualify_portfolio_files, render_portfolio_run


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        as_of = parse_review_point(args.as_of, "--as-of")
        run = qualify_portfolio_files(args.workspace, args.notices, as_of=as_of)
        sys.stdout.write(render_portfolio_run(run))
    except (SchemaValidationError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
