"""UI-neutral offline qualification workflow shared by all front ends."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

from ._version import __version__
from .demo_data import DEMO_AS_OF, demo_notices, demo_profile
from .models import (
    MAX_NOTICES_FILE_BYTES,
    MAX_PROFILE_FILE_BYTES,
    Notice,
    Profile,
    QualificationResult,
    notice_collection_from_file_bytes,
    notices_from_data,
    parse_iso_date,
    profile_from_dict,
    profile_from_json_bytes,
    read_bounded_file_bytes,
)
from .output import write_text_atomically
from .qualification import qualify_notices
from .report import ReportProvenance, render_html, render_markdown, report_as_dict


@dataclass(frozen=True, slots=True)
class QualificationRun:
    """One complete, deterministic qualification run."""

    profile: Profile
    as_of: date
    results: tuple[QualificationResult, ...]
    provenance: ReportProvenance

    @property
    def summary(self) -> dict[str, int]:
        payload = report_as_dict(
            self.profile,
            self.results,
            as_of=self.as_of,
            provenance=self.provenance,
        )
        return dict(cast(dict[str, int], payload["summary"]))


def qualify_inputs(
    profile: Profile,
    notices: Sequence[Notice],
    *,
    as_of: date,
    source_kind: str = "in_memory",
    profile_sha256: str | None = None,
    notices_sha256: str | None = None,
    ted_query: str | None = None,
    retrieved_at: str | None = None,
    lot_policy: str | None = None,
) -> QualificationRun:
    """Run the canonical offline rules against already validated inputs."""

    normalized_notices = tuple(notices)
    results = qualify_notices(profile, normalized_notices, as_of=as_of)
    provenance = ReportProvenance(
        generator_version=__version__,
        source_kind=source_kind,
        profile_sha256=profile_sha256 or _canonical_sha256(profile.to_dict()),
        notices_sha256=notices_sha256
        or _canonical_sha256([notice.to_dict() for notice in normalized_notices]),
        ted_query=ted_query,
        retrieved_at=retrieved_at,
        lot_policy=lot_policy,
    )
    return QualificationRun(
        profile=profile,
        as_of=as_of,
        results=results,
        provenance=provenance,
    )


def qualify_files(
    profile_path: str | Path,
    notices_path: str | Path,
    *,
    as_of: date,
) -> QualificationRun:
    """Load a JSON profile plus validated local CSV or JSON notices."""

    profile_payload = read_bounded_file_bytes(
        profile_path,
        MAX_PROFILE_FILE_BYTES,
        "profile",
    )
    notices_payload = read_bounded_file_bytes(
        notices_path,
        MAX_NOTICES_FILE_BYTES,
        "notices",
    )
    collection = notice_collection_from_file_bytes(notices_payload, notices_path)
    return qualify_inputs(
        profile_from_json_bytes(profile_payload, profile_path),
        collection.notices,
        as_of=as_of,
        source_kind=collection.source_kind,
        profile_sha256=_bytes_sha256(profile_payload),
        notices_sha256=_bytes_sha256(notices_payload),
        ted_query=collection.ted_query,
        retrieved_at=collection.retrieved_at,
        lot_policy=collection.lot_policy,
    )


def demo_run() -> QualificationRun:
    """Return the bundled, network-free synthetic run."""

    profile_data = demo_profile()
    notices_data = demo_notices()
    return qualify_inputs(
        profile_from_dict(profile_data),
        notices_from_data(notices_data),
        as_of=parse_iso_date(DEMO_AS_OF, "demo.as_of"),
        source_kind="synthetic_demo",
        profile_sha256=_canonical_sha256(profile_data),
        notices_sha256=_canonical_sha256(notices_data),
    )


def render_run(run: QualificationRun, format_name: str) -> str:
    """Render a completed run in one of the public output formats."""

    if format_name == "markdown":
        return render_markdown(
            run.profile,
            run.results,
            as_of=run.as_of,
            provenance=run.provenance,
        )
    if format_name == "html":
        return render_html(
            run.profile,
            run.results,
            as_of=run.as_of,
            provenance=run.provenance,
        )
    if format_name == "json":
        return dump_json(
            report_as_dict(
                run.profile,
                run.results,
                as_of=run.as_of,
                provenance=run.provenance,
            )
        )
    raise ValueError(f"unsupported format: {format_name}")


def write_run(run: QualificationRun, destination: str | Path, format_name: str) -> None:
    """Atomically export a completed run without changing its result order."""

    write_text_atomically(destination, render_run(run, format_name))


def dump_json(payload: object) -> str:
    """Serialize untrusted metadata without raw terminal or bidi controls."""

    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return _bytes_sha256(encoded)


def _bytes_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
