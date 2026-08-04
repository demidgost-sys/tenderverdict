"""Deterministic Markdown, HTML, and JSON-compatible report rendering."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
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
    as_of: date | datetime,
    provenance: ReportProvenance,
) -> dict[str, object]:
    """Return the canonical report structure shared by all renderers."""

    if type(as_of) is not date and not (type(as_of) is datetime and as_of.utcoffset() is not None):
        raise TypeError("as_of must be a date or a timezone-aware datetime")
    counts = _counts(results)
    return {
        "schema_version": 3,
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
    as_of: date | datetime,
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
        identity = _notice_identity(notice.publication_number, notice.lot_id)
        lines.extend(
            [
                "",
                f"## {_escape_markdown(identity)} — "
                f"{_escape_markdown(notice.title or '(title missing)')}",
                "",
                f"- **Verdict:** `{result.verdict.value}`",
                f"- **Buyer:** {_escape_markdown(notice.buyer or '(missing)')}",
                f"- **Deadline:** {_deadline_text(notice.deadline, notice.deadline_at)}",
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
    as_of: date | datetime,
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
  <title>TenderVerdict report: {company}</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-synthesis: none;
      line-height: 1.5;
      --page: #f2f4f8;
      --surface: #fbfcfe;
      --surface-raised: #f7f9fc;
      --text: #182132;
      --muted: #556278;
      --faint: #778298;
      --line: #d9e0ea;
      --accent: #4659c8;
      --accent-strong: #3548b5;
      --accent-soft: #edf0ff;
      --open: #0b6a4c;
      --open-soft: #dcf5ea;
      --watch: #765500;
      --watch-soft: #fff0bd;
      --reject: #962f40;
      --reject-soft: #fbe6eb;
      --radius-large: 1.25rem;
      --radius-medium: .75rem;
      --shadow: 0 1.5rem 4rem rgb(37 49 82 / .08), 0 .2rem .8rem rgb(37 49 82 / .05);
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --page: #10151e;
        --surface: #171d28;
        --surface-raised: #1c2431;
        --text: #f1f3f7;
        --muted: #b8c0ce;
        --faint: #929cad;
        --line: #313b4b;
        --accent: #9caaff;
        --accent-strong: #bdc5ff;
        --accent-soft: #252d4b;
        --open: #78d7b1;
        --open-soft: #143c31;
        --watch: #f1ca6f;
        --watch-soft: #403617;
        --reject: #ff9dad;
        --reject-soft: #46212a;
        --shadow: 0 1.5rem 4rem rgb(5 8 14 / .24), 0 .2rem .8rem rgb(5 8 14 / .18);
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ background: var(--page); }}
    body {{
      margin: 0;
      min-width: 18rem;
      color: var(--text);
      background: var(--page);
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }}
    main {{
      width: min(74rem, calc(100% - 3rem));
      margin: 0 auto;
      padding: clamp(2rem, 6vw, 5rem) 0 3rem;
    }}
    h1, h2, h3 {{
      margin-top: 0;
      line-height: 1.12;
      letter-spacing: -.025em;
      overflow-wrap: anywhere;
    }}
    .report-header {{
      max-width: 58rem;
      padding-bottom: clamp(1.75rem, 4vw, 3rem);
    }}
    .brand-line {{
      display: flex;
      align-items: center;
      gap: .7rem;
      margin-bottom: 1.4rem;
      color: var(--accent-strong);
      font-size: .9rem;
      font-weight: 750;
      letter-spacing: -.01em;
    }}
    .brand-mark {{
      display: inline-grid;
      width: 2.35rem;
      aspect-ratio: 1;
      place-items: center;
      border-radius: .85rem;
      color: #f7f8ff;
      background: var(--accent-strong);
      font-size: .72rem;
      letter-spacing: -.04em;
      box-shadow: inset 0 1px 0 rgb(247 248 255 / .2);
    }}
    h1 {{
      max-width: 16ch;
      margin-bottom: .8rem;
      font-size: clamp(2.35rem, 6vw, 4.6rem);
      font-weight: 780;
      letter-spacing: -.06em;
    }}
    .lede {{
      max-width: 62ch;
      margin: 0;
      color: var(--muted);
      font-size: clamp(1rem, 2vw, 1.18rem);
    }}
    time {{ white-space: nowrap; font-variant-numeric: tabular-nums; }}
    .summary {{
      display: grid;
      grid-template-columns: minmax(13rem, 1.35fr) repeat(3, minmax(8rem, .7fr));
      margin: 0 0 1rem;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: var(--radius-large);
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .summary-copy, .metric {{ padding: 1.3rem 1.4rem; }}
    .summary-copy {{
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: .25rem;
      background: var(--surface-raised);
    }}
    .summary-copy strong {{ font-size: 1.05rem; }}
    .summary-copy span {{ color: var(--muted); font-size: .88rem; }}
    .metric {{ border-left: 1px solid var(--line); }}
    .metric strong {{
      display: block;
      font-size: clamp(1.8rem, 4vw, 2.75rem);
      font-variant-numeric: tabular-nums;
      line-height: 1;
    }}
    .metric span {{ display: block; margin-top: .45rem; color: var(--muted); font-size: .88rem; }}
    .metric.open strong {{ color: var(--open); }}
    .metric.watch strong {{ color: var(--watch); }}
    .metric.reject strong {{ color: var(--reject); }}
    .results {{ display: grid; gap: 1.25rem; margin-top: 1.25rem; }}
    article {{
      padding: clamp(1.25rem, 4vw, 2rem);
      overflow-wrap: anywhere;
      border: 1px solid var(--line);
      border-radius: var(--radius-large);
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .result-header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 1rem 2rem;
      align-items: start;
    }}
    .notice-id {{
      margin: 0 0 .45rem;
      color: var(--faint);
      font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
      font-size: .78rem;
      font-weight: 650;
      letter-spacing: .015em;
    }}
    article h2 {{ margin-bottom: 0; font-size: clamp(1.35rem, 3vw, 1.85rem); }}
    dl.notice-meta {{
      display: grid;
      grid-template-columns:
        minmax(5.5rem, auto) minmax(0, 1fr)
        minmax(5.5rem, auto) minmax(0, 1fr);
      gap: .45rem 1rem;
      margin: 1.4rem 0 1.5rem;
      padding: 1rem 0;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; min-width: 0; overflow-wrap: anywhere; }}
    .verdict {{
      display: inline-flex;
      align-items: center;
      min-height: 2rem;
      border-radius: 999px;
      padding: .35rem .75rem;
      font-weight: 700;
      white-space: nowrap;
    }}
    .verdict.open_documents {{ color: var(--open); background: var(--open-soft); }}
    .verdict.watch {{ color: var(--watch); background: var(--watch-soft); }}
    .verdict.reject {{ color: var(--reject); background: var(--reject-soft); }}
    .evidence-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(14rem, .65fr);
      gap: 1.25rem 2rem;
    }}
    .evidence h3 {{ margin-bottom: .65rem; font-size: 1rem; letter-spacing: -.01em; }}
    .evidence ul {{ margin: 0; padding-left: 1.2rem; }}
    .evidence li + li {{ margin-top: .38rem; }}
    .next-step {{
      display: grid;
      grid-template-columns: 10rem minmax(0, 1fr);
      gap: .5rem 1rem;
      margin: 1.5rem 0 0;
      padding: 1rem 1.1rem;
      border: 1px solid color-mix(in srgb, var(--accent) 28%, var(--line));
      border-radius: var(--radius-medium);
      background: var(--accent-soft);
    }}
    .next-step strong {{ color: var(--accent-strong); }}
    .next-step span {{ min-width: 0; }}
    footer {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 2rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: .9rem;
    }}
    details.provenance {{
      margin: 1rem 0 1.25rem;
      border: 1px solid var(--line);
      border-radius: var(--radius-medium);
      background: var(--surface-raised);
    }}
    details.provenance summary {{
      cursor: pointer;
      padding: .9rem 1rem;
      color: var(--muted);
      font-weight: 700;
      transition: color 140ms ease;
    }}
    details.provenance summary:hover {{ color: var(--text); }}
    details.provenance dl {{
      display: grid;
      grid-template-columns: minmax(8rem, auto) minmax(0, 1fr);
      gap: .55rem 1rem;
      margin: 0;
      padding: 0 1rem 1rem;
    }}
    code {{
      color: var(--muted);
      font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
      font-size: .82em;
      overflow-wrap: anywhere;
    }}
    :focus-visible {{ outline: 3px solid var(--accent); outline-offset: 3px; }}
    @media (max-width: 48rem) {{
      main {{ width: min(100% - 2rem, 74rem); }}
      .summary {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .summary-copy {{ grid-column: 1 / -1; }}
      .metric {{ border-top: 1px solid var(--line); }}
      .metric:first-of-type {{ border-left: 0; }}
      dl.notice-meta {{ grid-template-columns: minmax(5.5rem, auto) minmax(0, 1fr); }}
      .evidence-grid {{ grid-template-columns: 1fr; }}
      .next-step {{ grid-template-columns: 1fr; }}
      footer {{ flex-direction: column; }}
    }}
    @media (max-width: 32rem) {{
      main {{ width: min(100% - 1rem, 74rem); padding: 1rem 0 2rem; }}
      h1 {{ font-size: clamp(2.1rem, 14vw, 3.25rem); }}
      .summary {{ grid-template-columns: 1fr; }}
      .summary-copy {{ grid-column: auto; }}
      .metric {{ border-top: 1px solid var(--line); border-left: 0; }}
      .result-header {{ grid-template-columns: 1fr; }}
      .verdict {{ justify-self: start; }}
      dl.notice-meta {{ grid-template-columns: 1fr; }}
      dl.notice-meta dd + dt {{ margin-top: .35rem; }}
    }}
    @media print {{
      :root {{
        color-scheme: light;
        --page: #f7f8fb;
        --surface: #fbfcfe;
        --surface-raised: #f7f9fc;
        --text: #182132;
        --muted: #556278;
        --faint: #778298;
        --line: #d9e0ea;
        --accent: #4659c8;
        --accent-strong: #3548b5;
        --accent-soft: #edf0ff;
      }}
      body {{ background: var(--page); }}
      main {{ width: 100%; padding: 0; }}
      article, .summary {{ box-shadow: none; break-inside: avoid; }}
      details.provenance {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main>
    <header class="report-header">
      <div class="brand-line">
        <span class="brand-mark" aria-hidden="true">TV</span><span>TenderVerdict</span>
      </div>
      <h1>Qualification report</h1>
      <p class="lede">
        Deterministic metadata review for {company}. Review point:
        <time datetime="{as_of.isoformat()}">{as_of.isoformat()}</time>.
      </p>
    </header>
    <section class="summary" aria-label="Verdict summary">
      <div class="summary-copy">
        <strong>Review outcomes</strong><span>{len(results)} notices assessed</span>
      </div>
      <div class="metric open">
        <strong>{counts[Verdict.OPEN_DOCUMENTS]}</strong><span>Open documents</span>
      </div>
      <div class="metric watch"><strong>{counts[Verdict.WATCH]}</strong><span>Watch</span></div>
      <div class="metric reject"><strong>{counts[Verdict.REJECT]}</strong><span>Reject</span></div>
    </section>
{provenance_html}
    <section class="results" aria-label="Qualification results">
{sections}    </section>
    <footer>
      <strong>TenderVerdict</strong>
      <span>
        Metadata-only decision support. No legal advice or autonomous participation decision.
      </span>
    </footer>
  </main>
</body>
</html>
"""


def _render_result_html(result: QualificationResult) -> str:
    notice = result.notice
    title = _escape_html_text(notice.title or "(title missing)")
    publication_number = _escape_html_text(
        _notice_identity(notice.publication_number, notice.lot_id)
    )
    buyer = _escape_html_text(notice.buyer or "(missing)")
    source = _escape_html_text(notice.source_url or "(missing)")
    deadline = _deadline_text(notice.deadline, notice.deadline_at)
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
    verdict_label = verdict.replace("_", " ").capitalize()
    return f"""      <article class="result verdict-{verdict}">
        <div class="result-header">
          <div><p class="notice-id">{publication_number}</p><h2>{title}</h2></div>
          <span class="verdict {verdict}">{verdict_label}</span>
        </div>
        <dl class="notice-meta">
          <dt>Buyer</dt><dd>{buyer}</dd>
          <dt>Deadline</dt><dd>{deadline}</dd>
          <dt>Published</dt><dd>{publication_date}</dd>
          <dt>Source</dt><dd>{source}</dd>
        </dl>
        <div class="evidence-grid">
          <section class="evidence"><h3>Reasons</h3><ul>{reasons}</ul></section>
          <section class="evidence"><h3>Unknowns</h3><ul>{unknowns}</ul></section>
        </div>
        <p class="next-step"><strong>Human next step</strong><span>{next_step}</span></p>
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


def _deadline_text(deadline: date | None, deadline_at: datetime | None) -> str:
    if deadline_at is not None:
        return deadline_at.isoformat()
    if deadline is not None:
        return deadline.isoformat()
    return "(missing)"


def _notice_identity(publication_number: str, lot_id: str | None) -> str:
    return f"{publication_number} / {lot_id}" if lot_id else publication_number


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
