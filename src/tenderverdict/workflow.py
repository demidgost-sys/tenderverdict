"""UI-neutral offline qualification workflow shared by all front ends."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

from .demo_data import DEMO_AS_OF, demo_notices, demo_profile
from .models import (
    Notice,
    Profile,
    QualificationResult,
    load_notices,
    load_profile,
    notices_from_data,
    parse_iso_date,
    profile_from_dict,
)
from .output import write_text_atomically
from .qualification import qualify_notices
from .report import render_html, render_markdown, report_as_dict


@dataclass(frozen=True, slots=True)
class QualificationRun:
    """One complete, deterministic qualification run."""

    profile: Profile
    as_of: date
    results: tuple[QualificationResult, ...]

    @property
    def summary(self) -> dict[str, int]:
        payload = report_as_dict(self.profile, self.results, as_of=self.as_of)
        return dict(cast(dict[str, int], payload["summary"]))


def qualify_inputs(
    profile: Profile,
    notices: Sequence[Notice],
    *,
    as_of: date,
) -> QualificationRun:
    """Run the canonical offline rules against already validated inputs."""

    results = qualify_notices(profile, tuple(notices), as_of=as_of)
    return QualificationRun(profile=profile, as_of=as_of, results=results)


def qualify_files(
    profile_path: str | Path,
    notices_path: str | Path,
    *,
    as_of: date,
) -> QualificationRun:
    """Load validated local JSON files and run the canonical offline rules."""

    return qualify_inputs(
        load_profile(profile_path),
        load_notices(notices_path),
        as_of=as_of,
    )


def demo_run() -> QualificationRun:
    """Return the bundled, network-free synthetic run."""

    return qualify_inputs(
        profile_from_dict(demo_profile()),
        notices_from_data(demo_notices()),
        as_of=parse_iso_date(DEMO_AS_OF, "demo.as_of"),
    )


def render_run(run: QualificationRun, format_name: str) -> str:
    """Render a completed run in one of the public output formats."""

    if format_name == "markdown":
        return render_markdown(run.profile, run.results, as_of=run.as_of)
    if format_name == "html":
        return render_html(run.profile, run.results, as_of=run.as_of)
    if format_name == "json":
        return dump_json(report_as_dict(run.profile, run.results, as_of=run.as_of))
    raise ValueError(f"unsupported format: {format_name}")


def write_run(run: QualificationRun, destination: str | Path, format_name: str) -> None:
    """Atomically export a completed run without changing its result order."""

    write_text_atomically(destination, render_run(run, format_name))


def dump_json(payload: object) -> str:
    """Serialize untrusted metadata without raw terminal or bidi controls."""

    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"
