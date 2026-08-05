# Next Gen UX and accessibility audit

- Audit date: 2026-08-05
- App surface: SwiftUI macOS app, default 1020×900 window
- Data boundary: local workspace JSON plus normalized CSV/JSON notices
- RevenueCat boundary: process-local Debug-only Test Store key; Release refuses configuration
  before the SDK; no usable key retained in the app or repo

## Verification vocabulary

This document deliberately separates four evidence levels:

| Label | Meaning |
|---|---|
| `code_verified` | The current source and contract were inspected; this is not a runtime claim. |
| `automated` | A deterministic check ran successfully on the current source revision. |
| `manual` | A human exercised the stated behavior on the dated packaged baseline. |
| `pending` | The current revision still needs the stated hands-on or artifact evidence. |

## Outcome

The current source closes the largest product gaps in the earlier aggregate-only portfolio demo.
A user can now build and validate profiles without hand-editing JSON, inspect a notice file before
analysis, opt into safe file-selection continuity, filter larger result sets, and move from a
Premium comparison cell to the exact profile/notice reasoning. The first complete analysis and
deterministic export remain free. The latest polish pass also makes demo/current/previous report
state explicit, validates the review point inline, gives the synthetic Free profile one example of
each verdict, separates verdict drivers from passed checks, and keeps stale export wording honest.
The winning-pass hierarchy now states the job in one sentence, surfaces a bounded Portfolio Signal
before the file controls, and explains the complete Free profile versus Portfolio value before the
technical RevenueCat build state. The static report uses the same open/verify/skip and human-owned
next-step vocabulary. The native Export menu now turns the accepted report into either deterministic
JSON or a self-contained human-review HTML brief: Free receives the complete first profile and
Premium receives every profile in source order.

The native suite now covers pure terminal RevenueCat accessibility outcomes in both Debug and
Release, and the complete Python/source gate passes on the current candidate. It also verifies that
untrusted control and bidirectional-formatting characters become visible in SwiftUI, that Free
exports one complete schema-3 report and a gated review brief, and that Release cannot reach Test
Store SDK configuration. Exact totals and packaged provenance live in
[project status](PROJECT_STATUS.md). The prior packaged
Debug baseline still provides genuine RevenueCat Test Store and VoiceOver Restore evidence, but it
predates the newest UX changes. The current portrait asset has been regenerated and reviewed in
light and dark appearance. The current Release package rendered both native appearances and both
review-brief projections outside the worktree; the previous Release package remains the latest
hands-on compact Profile Builder and invalid-CPV recovery pass. A fresh Debug transaction build and
manual VoiceOver checks for asynchronous purchase outcomes remain pending.

## Current source audit (`code_verified`)

| Surface | Outcome | Boundary checked |
|---|---|---|
| Profile Builder | Pass | Creates, removes, and reorders 1–5 profiles; edits name, CPV codes, countries, and minimum lead time; rejects malformed or duplicate names; validates through the bundled Python authority tables before atomic Save As. |
| Workspace contract | Pass | Schema 1 only, strict unknown-field rejection, 256 KiB bound, deterministic normalized JSON, profile order preserved. |
| Notice import preview | Pass | Accepts normalized CSV or JSON, shows source type, total count, first five records, warnings, and full-file missing-field counts before analysis. It does not invent arbitrary column mapping. |
| Input failure retention | Pass | Invalid workspace or notices remain an input error; the last valid report/export is not replaced. |
| Report truth state | Pass | Synthetic, current selected-input, and retained previous reports have distinct visible context; previous export remains possible but is explicitly labelled in the action and Save panel. |
| Review-point recovery | Pass | Strict date/RFC-3339 validation appears inline, **Use today** supplies a local calendar date, and an invalid value does not launch the child process. |
| Local continuity | Pass | Explicit opt-in persists only security-scoped bookmarks for workspace and notices. Turning it off removes the bookmarks. It never stores tender contents, reports, `as_of`, or the RevenueCat key, and restored files do not auto-run. |
| Free review queue | Pass | Text search covers notice/lot ID, title, and buyer; buyer, deadline-presence, and verdict filters compose; results load in bounded pages; Clear resets every filter, and a changed report identity resets state. |
| Explanation hierarchy | Pass | Existing reason order is preserved in exports while native disclosure presents verdict drivers, confirmation items, and routine passed checks as separate groups. |
| Stable large-list identity | Pass | Filters retain canonical result IDs; a filtered offset is never reused as a cross-profile lookup key. |
| Premium comparison | Pass | Text, buyer, and deadline filters apply to the shared notice order; each cell is a native button with profile, notice, and verdict semantics; locked state reveals only the bounded disagreement count. |
| Comparison drill-down | Pass | A selected cell resolves by stable profile/result IDs and shows verdict, buyer, deadline, next step, reasons, unknowns, and only a safe supplied HTTPS source. |
| Untrusted display text | Pass | C0, DEL/C1, and Unicode format controls are visibly escaped in native text and accessibility labels; source evidence and deterministic export bytes are preserved. |
| Review brief export | Pass | The native Export menu offers deterministic JSON and self-contained HTML. Free HTML contains only the complete first profile; Premium HTML contains every profile in original order. The renderer adds no script, remote asset, telemetry, combined verdict, ranking, or new qualification rule; text is normalized/escaped and only validated HTTPS sources become links. |
| RevenueCat projection | Pass | `supplier_profiles_plus` changes only native visibility. Free exports the first complete schema-3 report and first-profile brief; Premium exports the exact portfolio bytes and all-profile brief. Neither path modifies qualification bytes, adds rankings, or creates a local entitlement toggle. |
| RevenueCat configuration | Pass | Debug accepts only a well-shaped process-local Test Store key and an exact offering/package/product match. Release exposes no key field and refuses configuration before any SDK call. |
| Async recovery model | Pass | Every terminal Premium state has explicit announcement text, recovery actions, and a useful focus target. Focus restoration occurs only after a user-triggered connect/purchase/restore/refresh action. |
| Responsive layout | Pass | Fixed hero typography uses semantic `largeTitle`; input, action, RevenueCat, metadata, filter, and detail rows use horizontal-to-vertical fallbacks; Profile Builder keeps message and action areas separate so its footer does not create a vertical spacer gap. |
| Contrast/transparency response | Pass | Semantic card boundaries strengthen under Increase Contrast; decorative shadows/surfaces are reduced when Reduce Transparency is enabled. Textual state never relies on color alone. |

## Native contract checks (`automated`, current candidate passed)

The configuration-specific verification commands are:

```bash
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
swift run -c release --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
# expected from both: NEXT_GEN_CHECKS_OK (exact current total is in PROJECT_STATUS.md)
```

The checks cover:

- Free/Premium projection and schema-3 Free export isolation;
- complete notice-level result and provenance preservation;
- visible display normalization for control and bidi-formatting characters;
- strict review-point validation and deterministic **Use today** calendar semantics;
- verdict-driver/supporting-check separation and cross-profile disagreement counts;
- deterministic HTML-brief bytes, Free/Premium content isolation, profile/notice order, empty-state
  rendering, HTML/control escaping, restrictive CSP, and safe-link rejection;
- empty notice sets, profile counts, shared digests, and ordered shared metadata;
- nested verdict totals and result/summary consistency;
- strict, bounded, deterministic workspace and notice-preview documents;
- search/buyer/deadline filters, structured identities, and stable lookup across a synthetic
  125-notice result set;
- terminal Premium announcement, recovery-action, and focus outcomes;
- exact RevenueCat offering/package/product matching and Debug/Release fail-closed behavior;
- process-adapter deterministic byte preservation and size caps.

These checks validate contracts and pure state. They do not claim AppKit rendering quality, an
actual RevenueCat transaction, or VoiceOver speech.

The clean release-configuration package named in project status passed
configuration-specific native checks, embedded normalization and import-preview contracts twice
with byte-identical output, ad-hoc signature verification, and app smoke from outside the worktree.
It also rendered the Free and Premium HTML projections plus both native appearances from `/`, then
produced the `.app`, zip, and verified SHA-256 companion on a regenerable SSD path. Release is the
no-key evaluation artifact and cannot substitute for the pending Debug Test Store pass. Exact
current provenance lives in [project status](PROJECT_STATUS.md).

## Current review-brief pass (`automated` + visual inspection, 2026-08-05)

The exact clean Release artifact named in project status was exercised through headless paths that
use the same renderer as the app's Export menu. This is current packaged rendering evidence, not a
claim that the Save panel or Test Store transaction was exercised hands-on.

| Step | Current outcome |
|---|---|
| Native hierarchy | Packaged light and dark 1179×2556 renders show the compact **Export…** menu in the existing action row and explicitly include the review brief in the complete Free-profile promise. |
| HTML design continuity | The packaged Premium bytes matched the locally opened brief that was compared beside the current static schema-3 report. It preserves the same system typography, indigo accent, semantic outcome colors, card geometry, dark appearance, responsive structure, and human-next-step emphasis. |
| Free boundary | The packaged Free renderer emitted one complete profile and omitted the other profile names/details while explaining that its bounded disagreement count belongs to the full workspace. |
| Premium boundary | The packaged Premium renderer emitted all three synthetic profiles and their shared notices in source order, with independent per-profile counts only. |
| Safety and determinism | Repeated bytes are deterministic; injected markup is escaped; control/bidi characters remain visible; an unsafe URL never becomes a link; empty notices have an explicit state; no score, ranking, or automatic recommendation appears. |
| Process boundary | Rendering ran from `/` against the embedded core. No key, Test Store call, user file, or external destination was used. |

## Previous Release package (`manual`, 2026-08-05)

The exact clean `682c040` Release artifact was launched outside the worktree after the earlier
polish commit. This remains valid interaction evidence for unchanged flows, but it is not the
current artifact and not Test Store evidence because Release intentionally cannot accept a
RevenueCat key.

| Step | Current outcome |
|---|---|
| Opening hierarchy | The exact clean `682c040` package opened with “One tender feed. Different supplier decisions,” then showed 3 shared notices, 3 supplier profiles, and 2 changed outcomes before any file controls. |
| Main report state | Bundled demo context, one Open / one Watch / one Reject, the complete Free-profile promise, and the bounded two-of-three disagreement preview were visible. |
| Review queue | Search, buyer/deadline filters, all three verdict controls, notice cards, and human next steps remained legible at the default 1020×900 window. |
| Premium value | Free and Portfolio contents appeared before the Release/Test Store limitation; all three profiles and the disagreement count stayed visible without gated reasoning. |
| Compact Profile Builder | At a 680×714 sheet size, profile fields, status text, and footer actions remained visible without the former spacer gap. |
| Field recovery | Entering CPV `7226` and choosing **Validate** produced the specific eight-digit error in the profile card and footer. |
| Light/dark portrait | The exact 1179×2556 submission render was regenerated, metadata-stripped, and visually inspected in both appearances; the Portfolio Signal wraps without truncation. |
| Exit | The packaged app closed normally after inspection; no Test Store key or user data was entered. |

## Packaged baseline (`manual`, 2026-08-04)

The previous packaged Debug revision was exercised hands-on. This evidence remains useful for the
unchanged RevenueCat architecture, but must not be presented as a fresh-current-revision pass.

| Step | Baseline outcome |
|---|---|
| Worktree-independent launch | Embedded core loaded three profiles and three notices. |
| Selected local files | Native panels accepted the synthetic workspace and notices. |
| Deterministic export | Atomic export bytes matched canonical CLI output. |
| Invalid `as_of` | Specific error appeared and the previous valid report stayed exportable. |
| Missing key | Locked configuration UI appeared and no SDK request started. |
| Non-Test key | Rejected locally. |
| Test Store offering | Current monthly package loaded at localized `0,99 $`. |
| Cancellation | Access stayed locked with a recoverable state. |
| Failure and retry | Failure was explicit; retry returned to the offering. |
| Entitlement unlock | `supplier_profiles_plus` revealed every profile report and comparison. |
| Relaunch refresh | Re-entering the process-local key recovered the existing entitlement. |
| Restore | `restorePurchases()` kept access unlocked. |
| Dashboard readback | RevenueCat showed the sandbox subscription without retaining its anonymous customer identifier. |
| VoiceOver Restore | Restore was exposed and activated as a native button, then VoiceOver was switched off. |

These are Test Store outcomes with no real payment or App Store transaction.

## Visual and accessibility implementation

The visual language remains intentionally native: one indigo product accent, semantic verdict
colors plus text labels, 18–20 pt card radii, restrained depth, native controls, and progressive
reason disclosure. The hierarchy is now:

1. understand the job and the current shared-notice/profile disagreement signal;
2. build or choose a validated workspace;
3. choose notices, inspect the import preview, set a review point, and run locally;
4. search/filter the complete free first-profile review queue;
5. opt into file-bookmark continuity only if useful;
6. understand the complete Free versus Portfolio boundary before any purchase state;
7. unlock/filter the shared comparison and open exact cell reasoning;
8. export a deterministic human-review brief or JSON with current/previous state made explicit.

Accessibility-relevant code outcomes include distinct labels for secure configuration and file
actions, disabled-state preservation, combined profile summaries, native disclosures and links,
stable focus targets after Premium actions, VoiceOver announcements only when VoiceOver and a
visible app window are present, flexible row layouts, and Increased Contrast/Reduced Transparency
adaptation. Input-derived control and bidi-formatting characters are rendered visibly rather than
allowed to reorder evidence. Announcement content contains no key, customer identifier, or tender
data.

## Still required (`pending`)

1. Build a fresh Debug `.app` from the exact final revision and repeat the selected-file, both
   Save-panel export choices, and Test Store flow. Re-run the already-passing Release build only if
   the source changes afterward.
2. Manually inspect the remaining large-text, Increase Contrast, and Reduce Transparency states.
   The current light/dark portrait has already been regenerated and reviewed; regenerate it again
   only if later visual source changes are made.
3. With VoiceOver enabled, manually exercise Test Store purchase success, cancellation, failure,
   retry, and restore. Confirm each asynchronous announcement is spoken once and focus lands on the
   documented recovery control.
4. Preserve dated evidence without an API key, customer identifier, account email, or unrelated
   desktop content.

Until those steps pass, describe announcement routing and visual adaptation as implemented and
automated-contract-checked, not as fully hands-on verified on the final package.
