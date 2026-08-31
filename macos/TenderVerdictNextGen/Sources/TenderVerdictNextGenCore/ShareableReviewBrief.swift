import Foundation

public enum ReviewBriefError: Error, Equatable, LocalizedError {
  case outputTooLarge

  public var errorDescription: String? {
    switch self {
    case .outputTooLarge:
      return "The review brief is too large to export safely."
    }
  }
}

extension PortfolioWorkspaceReport {
  /// Renders a deterministic, self-contained HTML handoff for human review.
  ///
  /// Free access includes the complete first-profile review. Premium access includes every
  /// profile in source order. The brief is a presentation of the validated report only: it
  /// does not add scores, rankings, combined verdicts, or new qualification logic.
  public func shareableReviewBriefHTMLData(premiumUnlocked: Bool) throws -> Data {
    let html = ReviewBriefHTMLBuilder(
      report: self,
      premiumUnlocked: premiumUnlocked
    ).render()
    let data = Data((html + "\n").utf8)
    guard data.count <= ReviewBriefHTMLBuilder.maximumOutputBytes else {
      throw ReviewBriefError.outputTooLarge
    }
    return data
  }
}

private struct ReviewBriefHTMLBuilder {
  static let maximumOutputBytes = 64 * 1_024 * 1_024

  let report: PortfolioWorkspaceReport
  let premiumUnlocked: Bool

  private var visibleReports: [ProfileReport] {
    report.visibleProfileReports(premiumUnlocked: premiumUnlocked)
  }

  func render() -> String {
    let title =
      premiumUnlocked
      ? "TenderVerdict portfolio review brief"
      : "TenderVerdict profile review brief"
    let scopeTitle = premiumUnlocked ? "Complete portfolio review" : "First profile review"
    let scopeDetail =
      premiumUnlocked
      ? "All \(visibleReports.count) profiles are included in their original order."
      : "The complete first profile is included. \(report.divergentNoticeCount) of \(report.summary.noticeCount) shared notices change across the full workspace; other profile details are omitted."
    let profiles = visibleReports.enumerated().map(renderProfile).joined(separator: "\n")

    return """
      <!doctype html>
      <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="referrer" content="no-referrer">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; base-uri 'none'; form-action 'none'">
        <title>\(htmlEscaped(title))</title>
        <style>
          :root {
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
          }
          @media (prefers-color-scheme: dark) {
            :root {
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
            }
          }
          * { box-sizing: border-box; }
          html { background: var(--page); }
          body {
            margin: 0;
            min-width: 18rem;
            color: var(--text);
            background: var(--page);
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
          }
          main {
            width: min(74rem, calc(100% - 3rem));
            margin: 0 auto;
            padding: clamp(2rem, 6vw, 5rem) 0 3rem;
          }
          h1, h2, h3, h4 {
            margin-top: 0;
            line-height: 1.12;
            letter-spacing: -.025em;
            overflow-wrap: anywhere;
          }
          .report-header {
            max-width: 58rem;
            padding-bottom: clamp(1.75rem, 4vw, 3rem);
          }
          .brand-line {
            display: flex;
            align-items: center;
            gap: .7rem;
            margin-bottom: 1.4rem;
            color: var(--accent-strong);
            font-size: .9rem;
            font-weight: 750;
          }
          .brand-mark {
            display: inline-grid;
            width: 2.35rem;
            aspect-ratio: 1;
            place-items: center;
            border-radius: .85rem;
            color: #f7f8ff;
            background: var(--accent-strong);
            font-size: .72rem;
            letter-spacing: -.04em;
          }
          h1 {
            max-width: 16ch;
            margin-bottom: .8rem;
            font-size: clamp(2.35rem, 6vw, 4.6rem);
            font-weight: 780;
            letter-spacing: -.06em;
          }
          .lede {
            max-width: 64ch;
            margin: 0;
            color: var(--muted);
            font-size: clamp(1rem, 2vw, 1.18rem);
          }
          time { white-space: nowrap; font-variant-numeric: tabular-nums; }
          .summary {
            display: grid;
            grid-template-columns: minmax(15rem, 1.45fr) repeat(3, minmax(8rem, .7fr));
            margin-bottom: 2rem;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: var(--radius-large);
            background: var(--surface);
            box-shadow: var(--shadow);
          }
          .summary-copy, .metric { padding: 1.3rem 1.4rem; }
          .summary-copy {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: .25rem;
            background: var(--surface-raised);
          }
          .summary-copy strong { font-size: 1.05rem; }
          .summary-copy span, .metric span { color: var(--muted); font-size: .88rem; }
          .metric { border-left: 1px solid var(--line); }
          .metric strong {
            display: block;
            font-size: clamp(1.8rem, 4vw, 2.75rem);
            font-variant-numeric: tabular-nums;
            line-height: 1;
          }
          .metric span { display: block; margin-top: .45rem; }
          .profiles { display: grid; gap: 2.5rem; }
          .profile {
            padding: clamp(1.15rem, 3vw, 1.65rem);
            border: 1px solid var(--line);
            border-radius: calc(var(--radius-large) + .2rem);
            background: color-mix(in srgb, var(--accent-soft) 48%, var(--surface));
          }
          .profile-header {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 1rem 2rem;
            align-items: start;
            margin-bottom: 1rem;
          }
          .eyebrow {
            display: block;
            margin-bottom: .35rem;
            color: var(--accent-strong);
            font-size: .76rem;
            font-weight: 780;
            letter-spacing: .08em;
            text-transform: uppercase;
          }
          .profile h2 { margin-bottom: .55rem; font-size: clamp(1.6rem, 4vw, 2.35rem); }
          .profile-meta { margin: 0; color: var(--muted); overflow-wrap: anywhere; }
          .profile-counts {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: .45rem;
          }
          .count {
            padding: .32rem .65rem;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: var(--surface);
            color: var(--muted);
            font-size: .78rem;
            font-weight: 700;
            white-space: nowrap;
          }
          .results { display: grid; gap: 1.1rem; }
          article {
            padding: clamp(1.2rem, 4vw, 1.8rem);
            overflow-wrap: anywhere;
            border: 1px solid var(--line);
            border-radius: var(--radius-large);
            background: var(--surface);
            box-shadow: var(--shadow);
          }
          .result-header {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 1rem 2rem;
            align-items: start;
          }
          .notice-id {
            margin: 0 0 .45rem;
            color: var(--faint);
            font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
            font-size: .78rem;
            font-weight: 650;
          }
          article h3 { margin-bottom: 0; font-size: clamp(1.3rem, 3vw, 1.75rem); }
          .verdict {
            display: inline-flex;
            align-items: center;
            min-height: 2rem;
            border-radius: 999px;
            padding: .35rem .75rem;
            font-weight: 750;
            white-space: nowrap;
          }
          .verdict.open-documents { color: var(--open); background: var(--open-soft); }
          .verdict.verify { color: var(--watch); background: var(--watch-soft); }
          .verdict.skip { color: var(--reject); background: var(--reject-soft); }
          dl.notice-meta {
            display: grid;
            grid-template-columns: minmax(5.5rem, auto) minmax(0, 1fr) minmax(5.5rem, auto) minmax(0, 1fr);
            gap: .45rem 1rem;
            margin: 1.25rem 0 1.4rem;
            padding: 1rem 0;
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
          }
          dt { font-weight: 700; }
          dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
          .source-cell { display: flex; flex-wrap: wrap; gap: .2rem .65rem; align-items: baseline; }
          .source-link { color: var(--accent-strong); font-weight: 700; text-underline-offset: .16em; }
          .source-url { color: var(--muted); font-size: .82rem; }
          .evidence-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.25fr) minmax(14rem, .75fr);
            gap: 1.15rem 2rem;
          }
          .evidence h4 { margin-bottom: .6rem; font-size: .95rem; letter-spacing: -.01em; }
          .evidence ul { margin: 0; padding-left: 1.2rem; }
          .evidence li + li { margin-top: .35rem; }
          .quiet { color: var(--muted); }
          .next-step {
            display: grid;
            grid-template-columns: 10rem minmax(0, 1fr);
            gap: .5rem 1rem;
            margin: 1.4rem 0 0;
            padding: 1rem 1.1rem;
            border: 1px solid color-mix(in srgb, var(--accent) 28%, var(--line));
            border-radius: var(--radius-medium);
            background: var(--accent-soft);
          }
          .next-step strong { color: var(--accent-strong); }
          .empty {
            padding: 2rem;
            border: 1px dashed var(--line);
            border-radius: var(--radius-large);
            background: var(--surface);
            color: var(--muted);
            text-align: center;
          }
          footer {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-top: 2.5rem;
            padding-top: 1.25rem;
            border-top: 1px solid var(--line);
            color: var(--muted);
            font-size: .9rem;
          }
          :focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
          @media (max-width: 48rem) {
            main { width: min(100% - 2rem, 74rem); }
            .summary { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .summary-copy { grid-column: 1 / -1; }
            .metric { border-top: 1px solid var(--line); }
            .metric:first-of-type { border-left: 0; }
            .profile-header { grid-template-columns: 1fr; }
            .profile-counts { justify-content: flex-start; }
            dl.notice-meta { grid-template-columns: minmax(5.5rem, auto) minmax(0, 1fr); }
            .evidence-grid, .next-step { grid-template-columns: 1fr; }
            footer { flex-direction: column; }
          }
          @media (max-width: 32rem) {
            main { width: min(100% - 1rem, 74rem); padding: 1rem 0 2rem; }
            h1 { font-size: clamp(2.1rem, 14vw, 3.25rem); }
            .summary { grid-template-columns: 1fr; }
            .summary-copy { grid-column: auto; }
            .metric { border-left: 0; }
            .result-header { grid-template-columns: 1fr; }
            .verdict { justify-self: start; }
            dl.notice-meta { grid-template-columns: 1fr; }
          }
          @media print {
            :root {
              color-scheme: light;
              --page: #fff;
              --surface: #fff;
              --surface-raised: #f7f9fc;
              --text: #182132;
              --muted: #556278;
              --faint: #778298;
              --line: #d9e0ea;
              --accent: #4659c8;
              --accent-strong: #3548b5;
              --accent-soft: #edf0ff;
            }
            body { background: #fff; }
            main { width: 100%; padding: 0; }
            article, .summary, .profile { box-shadow: none; break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <main>
          <header class="report-header">
            <div class="brand-line"><span class="brand-mark" aria-hidden="true">TV</span><span>TenderVerdict · human review</span></div>
            <h1>What to open, verify, or skip.</h1>
            <p class="lede">A local, explainable review brief for one shared tender feed, evaluated at <time datetime="\(htmlEscaped(report.asOf))">\(htmlEscaped(report.asOf))</time>.</p>
          </header>
          <section class="summary" aria-label="Review scope">
            <div class="summary-copy"><strong>\(scopeTitle)</strong><span>\(scopeDetail)</span></div>
            <div class="metric"><strong>\(visibleReports.count)</strong><span>Profiles in brief</span></div>
            <div class="metric"><strong>\(report.summary.noticeCount)</strong><span>Shared notices</span></div>
            <div class="metric"><strong>\(report.divergentNoticeCount)</strong><span>Changed outcomes</span></div>
          </section>
          <section class="profiles" aria-label="Supplier profile reviews">
      \(profiles)
          </section>
          <footer><strong>TenderVerdict</strong><span>Metadata-only decision support. Human review remains required.</span></footer>
        </main>
      </body>
      </html>
      """
  }

  private func renderProfile(offset: Int, profileReport: ProfileReport) -> String {
    let profile = profileReport.profile
    let position = offset + 1
    let countries = profile.countries.map(htmlEscaped).joined(separator: ", ")
    let cpvCodes = profile.cpvCodes.map(htmlEscaped).joined(separator: ", ")
    let results =
      profileReport.results.isEmpty
      ? "<div class=\"empty\">No notices were included at this review point.</div>"
      : profileReport.results.map(renderResult).joined(separator: "\n")

    return """
            <section class="profile" aria-labelledby="profile-\(position)">
              <div class="profile-header">
                <div>
                  <span class="eyebrow">Supplier profile \(position)</span>
                  <h2 id="profile-\(position)">\(htmlEscaped(profile.displayName))</h2>
                  <p class="profile-meta">CPV \(cpvCodes) · Countries \(countries) · Minimum lead time \(profile.minimumDaysToDeadline) days</p>
                </div>
                <div class="profile-counts" aria-label="Profile verdict counts">
                  <span class="count">\(profileReport.summary.openDocuments) open</span>
                  <span class="count">\(profileReport.summary.watch) verify</span>
                  <span class="count">\(profileReport.summary.reject) skip</span>
                </div>
              </div>
              <div class="results">
      \(results)
              </div>
            </section>
      """
  }

  private func renderResult(_ result: QualificationResult) -> String {
    let presentation = verdictPresentation(result.verdict)
    let drivers = renderList(
      result.displayVerdictDrivers,
      empty: "No exception-driving reason in the supplied metadata."
    )
    let unknowns = renderList(
      result.displayUnknowns,
      empty: "Nothing else was flagged for confirmation."
    )
    let source = renderSource(result)

    return """
                <article>
                  <div class="result-header">
                    <div><p class="notice-id">\(htmlEscaped(result.displayReference))</p><h3>\(htmlEscaped(result.displayTitle))</h3></div>
                    <span class="verdict \(presentation.cssClass)">\(presentation.label)</span>
                  </div>
                  <dl class="notice-meta">
                    <dt>Buyer</dt><dd>\(htmlEscaped(result.displayBuyer))</dd>
                    <dt>Deadline</dt><dd>\(htmlEscaped(result.displayDeadline))</dd>
                    <dt>Source</dt><dd class="source-cell">\(source)</dd>
                  </dl>
                  <div class="evidence-grid">
                    <section class="evidence"><h4>Verdict drivers</h4>\(drivers)</section>
                    <section class="evidence"><h4>Needs confirmation</h4>\(unknowns)</section>
                  </div>
                  <p class="next-step"><strong>Next human step</strong><span>\(htmlEscaped(result.displayHumanNextStep))</span></p>
                </article>
      """
  }

  private func renderList(_ values: [String], empty: String) -> String {
    guard !values.isEmpty else {
      return "<p class=\"quiet\">\(htmlEscaped(empty))</p>"
    }
    let items = values.map { value in "<li>\(htmlEscaped(value))</li>" }.joined()
    return "<ul>\(items)</ul>"
  }

  private func renderSource(_ result: QualificationResult) -> String {
    guard let sourceURL = result.safeSourceURL else {
      return "<span class=\"quiet\">No verified HTTPS link supplied</span>"
    }
    let escapedURL = htmlEscaped(sourceURL.absoluteString)
    return """
      <a class="source-link" href="\(escapedURL)" target="_blank" rel="noopener noreferrer">Open supplied source</a><span class="source-url">\(escapedURL)</span>
      """
  }

  private func verdictPresentation(_ verdict: QualificationVerdict) -> (
    label: String, cssClass: String
  ) {
    switch verdict {
    case .openDocuments:
      return ("Open documents", "open-documents")
    case .watch:
      return ("Verify", "verify")
    case .reject:
      return ("Skip", "skip")
    }
  }

  private func htmlEscaped(_ value: String) -> String {
    normalizedDisplayText(value)
      .replacingOccurrences(of: "&", with: "&amp;")
      .replacingOccurrences(of: "<", with: "&lt;")
      .replacingOccurrences(of: ">", with: "&gt;")
      .replacingOccurrences(of: "\"", with: "&quot;")
      .replacingOccurrences(of: "'", with: "&#39;")
  }
}
