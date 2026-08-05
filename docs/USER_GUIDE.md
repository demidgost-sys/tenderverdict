# User guide

TenderVerdict turns supplied public-procurement notice metadata into an explainable local review
queue. Choose the surface that matches the job:

| Surface | Best for | Output |
|---|---|---|
| `tenderverdict demo` | First reproducible run | Markdown, HTML, or JSON |
| `tenderverdict qualify` | One supplier profile | Schema-3 JSON, Markdown, or HTML |
| Tk desktop | Interactive single-profile review | JSON, Markdown, or HTML |
| `tenderverdict portfolio` | Automation across one to five profiles | Portfolio schema-1 JSON |
| TenderVerdict Next Gen | Native macOS Portfolio Workspace demo | Free first profile, RevenueCat-backed Premium portfolio, HTML review brief or JSON |

## Next Gen first run

1. Launch the app. The bundled three-profile synthetic example runs locally and shows the first
   profile in the Free section with one Open, one Watch, and one Reject. The **Bundled demo
   report** banner keeps synthetic evidence distinct from a selected-input run. The **Portfolio
   Signal** above the inputs states how many shared notices change verdict across profiles without
   revealing the gated reports or ranking profiles.
2. To create your own workspace, select **Build profiles…**. Add, remove, or reorder one to five
   profiles, then use **Validate & Save As…**. The app first checks the fields, then asks the
   canonical Python parser to normalize and validate the complete workspace before saving it.
   Alternatively, choose an existing workspace v1 JSON file; it passes through the same parser.
3. Choose normalized notices in CSV or JSON. The complete file is validated before it becomes
   runnable. Confirm the displayed format, total count, first five normalized records, visible
   metadata-warning summary, and full-file missing-field counts.
4. Enter a review point as `YYYY-MM-DD` or the supported whole-second RFC 3339 form
   (`YYYY-MM-DDTHH:MM:SSZ` or an explicit UTC offset, without fractional seconds), or select **Use
   today**. Invalid calendar values are explained inline before the core runs. Select **Run
   portfolio**. A successful result updates the source label, review point, summary, and Free
   profile. Choosing another accepted input, changing the review point, or starting a rerun labels
   the last result **Previous report kept for reference** until a successful result replaces it. A
   failed analysis does not discard those previous valid bytes.
5. Narrow the Free queue by verdict, text, buyer, or whether a deadline was supplied. Use
   **Show more** to reveal the next bounded group, expand **Why this verdict**, and inspect verdict
   drivers, items needing confirmation, and routine checks separately. **Clear filters** resets the
   verdict filter too, and loading a different report resets the complete filter state. Open a
   syntactically safe supplied HTTPS source when the official notice needs inspection.
6. Open **Export…** and choose the handoff you need. **Export review brief…** saves a deterministic,
   self-contained HTML file with verdict drivers, confirmation items, safe source links, and each
   next human step. Free includes the complete first profile only; active Premium includes every
   profile in source order. **Export JSON…** saves the deterministic ASCII-safe schema-3 first
   profile in Free or the exact complete portfolio bytes in Premium. A retained older result stays
   exportable by design, but the menu and Save panel explicitly say **previous**.
7. Optional: enable **Remember these two file selections on this Mac**. This persists only the two
   security-scoped bookmarks. Relaunch validates the restored selections but never analyzes them
   automatically. Disable the toggle to forget the bookmarks.
8. The Premium card compares the packaging before asking for a purchase: Free includes one complete
   profile with reasons, its review brief, and JSON; Portfolio includes up to five profiles, the
   shared comparison, the complete portfolio brief, and full portfolio JSON. For the Shipaton Test
   Store demo, use the separately packaged Debug app and paste a RevenueCat
   `test_` key. TenderVerdict does not store it. The release-configuration app disables key entry
   before the SDK can reject it. Use the exact expected offering/package/product or restore access;
   the cross-profile comparison, all profile summaries, and full portfolio export appear only while
   `supplier_profiles_plus` is active. Before purchase, the locked preview can disclose how many
   shared notices produce different verdicts without exposing the gated reports. **Refresh
   offering** retries a recoverable network or
   dashboard issue. If an already configured key/project is wrong, quit and reopen the Debug app to
   replace it because the RevenueCat SDK can be configured only once per process.

The Shipaton Manager confirmed both that a Test Store purchase is sufficient for judging and that
a macOS entry has no judging disadvantage: [Test Store answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient) and
[macOS answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission).

The open-source CLI stays usable without Premium. The native Premium experience is a product and
competition integration boundary, not encryption or DRM.

## Workspace input

```json
{
  "schema_version": 1,
  "profiles": [
    {
      "schema_version": 1,
      "name": "Example Austria Services",
      "cpv_codes": ["72260000"],
      "countries": ["AUT"],
      "minimum_days_to_deadline": 14
    }
  ]
}
```

- Use one to five profiles.
- Names are trimmed and must be unique without regard to case.
- Unknown fields, invalid codes, unsupported versions, or one invalid profile reject the complete
  workspace.
- The workspace file is bounded to 256 KiB.
- The builder accepts comma-, semicolon-, whitespace-, or newline-separated code values, removes
  exact duplicates, uppercases countries, and preserves profile order. Final authority-table and
  schema validation still happens in the Python core.

Notice format and limits are documented in the root [README](../README.md). A notice file can hold
at most 1,000 records and 10 MiB. Treat every report as a metadata review aid, then inspect the
current official notice and procurement documents.

Supported competition `notice_type` values are `competition`, `competition notice`,
`contract notice`, `cn-social`, and `cn-standard` after case/whitespace normalization. A missing
type becomes `watch`; another supplied type becomes `reject`.

## Notice import preview

Choosing notices runs the same bounded parser used for qualification; preview is not a separate
permissive import path. The app shows at most the first five normalized records but computes the
record total and missing-field counts across the complete file. The counted fields are notice type,
title, buyer, CPV codes, countries, deadline (`deadline` or `deadline_at`), and source URL.

The normalized preview contract also carries publication/lot identity, publication date, metadata
warnings, and the fixed canonical field list. An invalid suffix, malformed UTF-8/CSV/JSON,
unsupported value, duplicate notice identity, oversized file, or other schema failure leaves the
previous selection and report intact and shows an actionable error.

Warnings attached to the previewed records remain available on each row and are also collected
under a visible **metadata warnings in preview** disclosure, so they are not discoverable only by
pointer hover.

## Understanding the result

- `open_documents`: configured metadata checks passed; open the official documents.
- `watch`: a broader match, missing field, or time boundary needs human resolution.
- `reject`: a configured hard metadata stop applies.

These are workflow states, not legal conclusions. Portfolio Workspace never compares or ranks
profiles. Premium's matrix aligns the same ordered notices across profiles so a human can see where
outcomes differ; it does not compute a winner. Search, buyer, and deadline filters are applied to
the shared primary notice identities. Selecting a verdict cell resolves the matching result by its
stable profile/result IDs—not by a filtered row offset—and opens the profile, notice metadata,
reasons, unknowns, human next step, and safe source link.

The native presentation groups the existing reason strings into **Verdict drivers**, **Needs
confirmation**, and **Checks passed**. This grouping is derived presentation only: exported reason
order, verdict semantics, schemas, and hashes remain unchanged. A Reject next step means the notice
does not fit that profile under the recorded hard-stop evidence; it does not presume that valid
source metadata is erroneous.

The HTML review brief is another presentation of the accepted report, not a new report schema. It
contains no scripts, remote assets, telemetry, combined verdict totals, ranking, or automatic
recommendation. A restrictive content-security policy is embedded in the file, untrusted display
text is escaped after control-character normalization, and only syntactically safe HTTPS source
URLs become links. It remains a metadata handoff that requires human review.

## Privacy and credentials

- `demo`, `qualify`, and `portfolio` do not make network requests.
- The Next Gen app runs profile and notice analysis through its private offline bridge. Source
  builds launch `tools/next_gen_core_launcher.py`; packaged builds freeze the same launcher as
  `TenderVerdictCore`. Neither path uses a shell.
- File contents are not sent to RevenueCat.
- A Test Store key enables normal RevenueCat SDK network activity. The in-app field is secure and
  process-only; no key is committed or written to TenderVerdict settings.
- The optional continuity setting stores only two macOS security-scoped bookmarks in app defaults.
  It does not persist tender contents, generated reports, the review point, or the RevenueCat key,
  and it does not auto-run remembered files.
- After explicit configuration, RevenueCat receives the identifiers and Test Store operations
  normally used by its SDK. That network boundary is separate from TenderVerdict's offline input
  and report path.
- Keep confidential tender documents outside this alpha. The product is designed for normalized
  notice metadata, not full-document ingestion.

## Accessibility and recovery

The macOS app uses native labelled buttons, text fields, a secure field, visible focus, text plus
icons for status, and a linear keyboard order. Profile cards expose one combined VoiceOver label
with the name and all three verdict counts. Notice verdicts and comparison cells include text labels
instead of relying on color. Terminal RevenueCat states have explicit VoiceOver announcements and
recovery targets; focus returns to purchase, retry, restore, or the key field only after a related
user action, not an automatic launch refresh. Cards adapt their borders/fills for Increase Contrast
and remove decorative transparency/shadows when Reduce Transparency is active.

Those paths are implemented, and the clean packages named in project status passed their embedded-
core, signature, checksum, ZIP, and worktree-independent smoke checks. The fresh `3cf20ed` Debug
pass covered keyboard order, Increase Contrast, Reduce Transparency, large-text rendering, and the
current purchase/cancel/failure/retry/restore/relaunch states. VoiceOver was deliberately excluded
to keep that pass silent. The previous Debug baseline remains the latest evidence that VoiceOver
exposed the transaction controls and activated Restore; current spoken announcements/focus still
require a dedicated pass before submission.

If a run fails, correct the displayed input error and run again. The last valid report remains
available and visibly marked as previous; exporting it never silently presents it as current. If
Premium refresh fails, verify the RevenueCat entitlement, exact offering/package/
product, Test Store connection, and key, then retry or restore; relaunch to replace a configured key.
