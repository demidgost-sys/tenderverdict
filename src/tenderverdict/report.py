"""Deterministic Markdown, HTML, and JSON-compatible report rendering."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from html import escape as escape_html
from unicodedata import category

from .models import Profile, QualificationResult, Verdict


@dataclass(frozen=True, slots=True)
class ReportProvenance:
    """Stable generator and input evidence attached to every product report."""

    generator_version: str
    source_kind: str
    profile_sha256: str
    notices_sha256: str
    ted_query: str | None = None
    retrieved_at: str | None = None
    lot_policy: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "generator": {"name": "TenderVerdict", "version": self.generator_version},
            "source_kind": self.source_kind,
            "profile_sha256": self.profile_sha256,
            "notices_sha256": self.notices_sha256,
        }
        if self.ted_query is not None:
            payload["ted_query"] = self.ted_query
        if self.retrieved_at is not None:
            payload["retrieved_at"] = self.retrieved_at
        if self.lot_policy is not None:
            payload["lot_policy"] = self.lot_policy
        return payload


def report_as_dict(
    profile: Profile,
    results: Sequence[QualificationResult],
    as_of: date,
    provenance: ReportProvenance,
) -> dict[str, object]:
    """Return the canonical report structure shared by all renderers."""

    if type(as_of) is not date:
        raise TypeError("as_of must be a datetime.date")
    counts = _counts(results)
    return {
        "schema_version": 2,
        "provenance": provenance.to_dict(),
        "profile": profile.to_dict(),
        "as_of": as_of.isoformat(),
        "summary": {
            "total": len(results),
            Verdict.OPEN_DOCUMENTS.value: counts[Verdict.OPEN_DOCUMENTS],
            Verdict.WATCH.value: counts[Verdict.WATCH],
            Verdict.REJECT.value: counts[Verdict.REJECT],
        },
        "results": [result.to_dict() for result in results],
    }


def render_markdown(
    profile: Profile,
    results: Sequence[QualificationResult],
    as_of: date,
    provenance: ReportProvenance,
) -> str:
    """Render a stable Markdown report with untrusted values escaped."""

    counts = _counts(results)

    lines = [
        "# TenderVerdict qualification report",
        "",
        f"- **Company:** {_escape_markdown(profile.name)}",
        f"- **As of:** {as_of.isoformat()}",
        f"- **Notices:** {len(results)}",
        "",
        "## Provenance",
        "",
        f"- **Generator:** TenderVerdict {provenance.generator_version}",
        f"- **Source kind:** {_escape_markdown(provenance.source_kind)}",
        f"- **Profile SHA-256:** `{provenance.profile_sha256}`",
        f"- **Notices SHA-256:** `{provenance.notices_sha256}`",
    ]

    if provenance.ted_query is not None:
        lines.append(f"- **TED query:** {_escape_markdown(provenance.ted_query)}")
    if provenance.retrieved_at is not None:
        lines.append(f"- **Retrieved at:** `{provenance.retrieved_at}`")
    if provenance.lot_policy is not None:
        lines.append(f"- **Lot policy:** `{provenance.lot_policy}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **open_documents:** {counts[Verdict.OPEN_DOCUMENTS]}",
            f"- **watch:** {counts[Verdict.WATCH]}",
            f"- **reject:** {counts[Verdict.REJECT]}",
        ]
    )

    for result in results:
        notice = result.notice
        lines.extend(
            [
                "",
                f"## {_escape_markdown(notice.publication_number)} — "
                f"{_escape_markdown(notice.title or '(title missing)')}",
                "",
                f"- **Verdict:** `{result.verdict.value}`",
                f"- **Buyer:** {_escape_markdown(notice.buyer or '(missing)')}",
                "- **Deadline:** "
                f"{notice.deadline.isoformat() if notice.deadline else '(missing)'}",
                "- **Published:** "
                + (notice.publication_date.isoformat() if notice.publication_date else "(missing)"),
                f"- **Source:** {_escape_markdown(notice.source_url or '(missing)')}",
                "",
                "### Reasons",
                "",
            ]
        )
        lines.extend(f"- {_escape_markdown(reason)}" for reason in result.reasons)
        lines.extend(["", "### Unknowns", ""])
        if result.unknowns:
            lines.extend(f"- {_escape_markdown(unknown)}" for unknown in result.unknowns)
        else:
            lines.append("- None from the supplied metadata.")
        lines.extend(
            [
                "",
                f"**Human next step:** {_escape_markdown(result.human_next_step)}",
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "Metadata-only decision support. No legal advice and no autonomous "
            "participation decision.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(
    profile: Profile,
    results: Sequence[QualificationResult],
    as_of: date,
    provenance: ReportProvenance,
) -> str:
    """Render a self-contained static HTML report without scripts or remote assets."""

    counts = _counts(results)

    sections = "".join(_render_result_html(result) for result in results)
    company = _escape_html_text(profile.name)
    provenance_html = _render_provenance_html(provenance)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="referrer" content="no-referrer">
  <title>TenderVerdict report — {company}</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.5; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: #172033; background: #f5f7fa; }}
    main {{ width: min(70rem, calc(100% - 2rem)); margin: 0 auto; padding: 2.5rem 0; }}
    h1, h2, h3 {{ line-height: 1.2; overflow-wrap: anywhere; }}
    .lede {{ max-width: 70ch; color: #44516a; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(12rem, 100%), 1fr));
      gap: .75rem;
      margin: 1.5rem 0;
    }}
    .metric, article {{ border: 1px solid #d8dfeb; border-radius: .75rem; background: #fff; }}
    .metric {{ padding: 1rem; }}
    .metric strong {{ display: block; font-size: 1.5rem; }}
    article {{ margin: 1rem 0; padding: clamp(1rem, 3vw, 1.5rem); overflow-wrap: anywhere; }}
    dl {{ display: grid; grid-template-columns: minmax(7rem, auto) 1fr; gap: .35rem 1rem; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; min-width: 0; overflow-wrap: anywhere; }}
    .verdict {{
      display: inline-block;
      border-radius: 999px;
      padding: .2rem .65rem;
      font-weight: 700;
      background: #e8edf5;
    }}
    .open_documents {{ color: #075d45; background: #dff7ed; }}
    .watch {{ color: #765700; background: #fff2c7; }}
    .reject {{ color: #8a2030; background: #fde7ea; }}
    .next-step {{ border-left: .25rem solid #526df0; padding-left: .75rem; }}
    footer {{ margin-top: 2rem; color: #56627a; }}
    details.provenance {{ margin: 1rem 0 1.5rem; }}
    details.provenance summary {{ cursor: pointer; font-weight: 700; }}
    code {{ overflow-wrap: anywhere; }}
    @media (max-width: 32rem) {{
      main {{ width: min(100% - 1rem, 70rem); padding: 1rem 0; }}
      dl {{ grid-template-columns: 1fr; }}
      dd + dt {{ margin-top: .45rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>TenderVerdict qualification report</h1>
      <p class="lede">Metadata-only, deterministic decision support for {company}.
        As of {as_of.isoformat()}.</p>
    </header>
{provenance_html}
    <section class="summary" aria-label="Verdict summary">
      <div class="metric"><strong>{counts[Verdict.OPEN_DOCUMENTS]}</strong>
        open_documents</div>
      <div class="metric"><strong>{counts[Verdict.WATCH]}</strong>watch</div>
      <div class="metric"><strong>{counts[Verdict.REJECT]}</strong>reject</div>
    </section>
    <section aria-label="Qualification results">
{sections}    </section>
    <footer>Metadata-only decision support. No legal advice and no autonomous
      participation decision.</footer>
  </main>
</body>
</html>
"""


def _render_result_html(result: QualificationResult) -> str:
    notice = result.notice
    title = _escape_html_text(notice.title or "(title missing)")
    publication_number = _escape_html_text(notice.publication_number)
    buyer = _escape_html_text(notice.buyer or "(missing)")
    source = _escape_html_text(notice.source_url or "(missing)")
    deadline = notice.deadline.isoformat() if notice.deadline else "(missing)"
    publication_date = (
        notice.publication_date.isoformat() if notice.publication_date else "(missing)"
    )
    reasons = "".join(f"<li>{_escape_html_text(item)}</li>" for item in result.reasons)
    if result.unknowns:
        unknowns = "".join(f"<li>{_escape_html_text(item)}</li>" for item in result.unknowns)
    else:
        unknowns = "<li>None from the supplied metadata.</li>"
    next_step = _escape_html_text(result.human_next_step)
    verdict = result.verdict.value
    return f"""      <article>
        <h2>{publication_number} — {title}</h2>
        <p><span class="verdict {verdict}">{verdict}</span></p>
        <dl>
          <dt>Buyer</dt><dd>{buyer}</dd>
          <dt>Deadline</dt><dd>{deadline}</dd>
          <dt>Published</dt><dd>{publication_date}</dd>
          <dt>Source</dt><dd>{source}</dd>
        </dl>
        <h3>Reasons</h3>
        <ul>{reasons}</ul>
        <h3>Unknowns</h3>
        <ul>{unknowns}</ul>
        <p class="next-step"><strong>Human next step:</strong> {next_step}</p>
      </article>
"""


def _render_provenance_html(provenance: ReportProvenance) -> str:
    rows = [
        ("Generator", f"TenderVerdict {provenance.generator_version}"),
        ("Source kind", provenance.source_kind),
        ("Profile SHA-256", provenance.profile_sha256),
        ("Notices SHA-256", provenance.notices_sha256),
    ]
    if provenance.ted_query is not None:
        rows.append(("TED query", provenance.ted_query))
    if provenance.retrieved_at is not None:
        rows.append(("Retrieved at", provenance.retrieved_at))
    if provenance.lot_policy is not None:
        rows.append(("Lot policy", provenance.lot_policy))
    rendered = "".join(
        f"<dt>{_escape_html_text(label)}</dt><dd><code>{_escape_html_text(value)}</code></dd>"
        for label, value in rows
    )
    return (
        '    <details class="provenance">\n'
        "      <summary>Report provenance</summary>\n"
        f"      <dl>{rendered}</dl>\n"
        "    </details>"
    )


def _counts(results: Sequence[QualificationResult]) -> dict[Verdict, int]:
    counts = {verdict: 0 for verdict in Verdict}
    for result in results:
        counts[result.verdict] += 1
    return counts


def _escape_markdown(value: str) -> str:
    normalized = normalize_display_text(value)
    normalized = escape_html(normalized, quote=False)
    normalized = normalized.replace("\\", "\\\\")
    for character in "`*_{}[]()#+-.!|>":
        normalized = normalized.replace(character, f"\\{character}")
    return normalized


def _escape_html_text(value: str) -> str:
    return escape_html(normalize_display_text(value), quote=True)


def normalize_display_text(value: str) -> str:
    """Flatten structure and make terminal and bidi controls visible in any UI."""

    normalized: list[str] = []
    for character in value:
        codepoint = ord(character)
        if character in "\r\n\t":
            normalized.append(" ")
        elif codepoint < 0x20 or 0x7F <= codepoint <= 0x9F or category(character) == "Cf":
            escape = f"\\u{codepoint:04x}" if codepoint <= 0xFFFF else f"\\U{codepoint:08x}"
            normalized.append(escape)
        else:
            normalized.append(character)
    return " ".join("".join(normalized).split())
