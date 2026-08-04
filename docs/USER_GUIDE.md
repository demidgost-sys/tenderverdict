# User guide

TenderVerdict turns supplied public-procurement notice metadata into an explainable local review
queue. Choose the surface that matches the job:

| Surface | Best for | Output |
|---|---|---|
| `tenderverdict demo` | First reproducible run | Markdown, HTML, or JSON |
| `tenderverdict qualify` | One supplier profile | Schema-3 JSON, Markdown, or HTML |
| Tk desktop | Interactive single-profile review | JSON, Markdown, or HTML |
| `tenderverdict portfolio` | Automation across one to five profiles | Portfolio schema-1 JSON |
| TenderVerdict Next Gen | Native macOS Portfolio Workspace demo | Free first profile, RevenueCat-backed Premium portfolio, JSON export |

## Next Gen first run

1. Launch the app. The bundled three-profile synthetic example runs locally and shows the first
   profile in the Free section.
2. To use your own data, choose a workspace v1 JSON file and normalized notices in CSV or JSON.
3. Enter a review point as `YYYY-MM-DD` or a timezone-aware RFC 3339 instant.
4. Select **Run portfolio**. A successful result updates the source label, review point, summary,
   and Free profile.
5. Select **Export JSON…** to save the exact deterministic portfolio bytes. A failed analysis does
   not discard the previous valid result.
6. For an organizer-approved Test Store demo, paste a RevenueCat `test_` key. TenderVerdict does not
   store it. Use the current Test Store package or restore access; all profiles appear only while
   `supplier_profiles_plus` is active.

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

Notice format and limits are documented in the root [README](../README.md). A notice file can hold
at most 1,000 records and 10 MiB. Treat every report as a metadata review aid, then inspect the
current official notice and procurement documents.

## Understanding the result

- `open_documents`: configured metadata checks passed; open the official documents.
- `watch`: a broader match, missing field, or time boundary needs human resolution.
- `reject`: a configured hard metadata stop applies.

These are workflow states, not legal conclusions. Portfolio Workspace never compares or ranks
profiles.

## Privacy and credentials

- `demo`, `qualify`, and `portfolio` do not make network requests.
- The Next Gen app runs profile and notice analysis through its embedded offline core.
- File contents are not sent to RevenueCat.
- A Test Store key enables normal RevenueCat SDK network activity. The in-app field is secure and
  process-only; no key is committed or written to TenderVerdict settings.
- Keep confidential tender documents outside this alpha. The product is designed for normalized
  notice metadata, not full-document ingestion.

## Accessibility and recovery

The macOS app uses native labelled buttons, text fields, a secure field, visible focus, text plus
icons for status, and a linear keyboard order. Profile cards expose one combined VoiceOver label
with the name and all three verdict counts. Hands-on VoiceOver transaction testing remains pending.

If a run fails, correct the displayed input error and run again. The last valid report remains
available. If Premium refresh fails, verify the RevenueCat entitlement, current offering, Test
Store connection, and key, then retry or restore.
