# Next Gen UX and accessibility audit

- Audit date: 2026-08-05
- App surface: SwiftUI macOS app, default 1020×900 window
- Data boundary: local workspace JSON plus normalized CSV/JSON notices
- RevenueCat boundary: process-local Test Store key; no usable key retained in the app or repo

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
deterministic export remain free.

The native suite now contains 15 checks, including a pure terminal RevenueCat accessibility-outcome
check, and a fresh worktree-independent Release package passes on the current app source. The final
15-check execution and complete 122-test Python suite pass on the current candidate. The prior packaged Debug
baseline still provides genuine RevenueCat Test Store and VoiceOver Restore evidence, but it
predates the newest UX changes. The current portrait asset has been regenerated and reviewed in
light and dark appearance; a fresh Debug transaction build and manual VoiceOver checks for
asynchronous purchase outcomes remain pending.

## Current source audit (`code_verified`)

| Surface | Outcome | Boundary checked |
|---|---|---|
| Profile Builder | Pass | Creates, removes, and reorders 1–5 profiles; edits name, CPV codes, countries, and minimum lead time; rejects malformed or duplicate names; validates through the bundled Python authority tables before atomic Save As. |
| Workspace contract | Pass | Schema 1 only, strict unknown-field rejection, 256 KiB bound, deterministic normalized JSON, profile order preserved. |
| Notice import preview | Pass | Accepts normalized CSV or JSON, shows source type, total count, first five records, warnings, and full-file missing-field counts before analysis. It does not invent arbitrary column mapping. |
| Input failure retention | Pass | Invalid workspace or notices remain an input error; the last valid report/export is not replaced. |
| Local continuity | Pass | Explicit opt-in persists only security-scoped bookmarks for workspace and notices. Turning it off removes the bookmarks. It never stores tender contents, reports, `as_of`, or the RevenueCat key, and restored files do not auto-run. |
| Free review queue | Pass | Text search covers notice/lot ID, title, and buyer; buyer, deadline-presence, and verdict filters compose; results load in bounded pages and can be reset. |
| Stable large-list identity | Pass | Filters retain canonical result IDs; a filtered offset is never reused as a cross-profile lookup key. |
| Premium comparison | Pass | Text, buyer, and deadline filters apply to the shared notice order; each cell is a native button with profile, notice, and verdict semantics. |
| Comparison drill-down | Pass | A selected cell resolves by stable profile/result IDs and shows verdict, buyer, deadline, next step, reasons, unknowns, and only a safe supplied HTTPS source. |
| RevenueCat projection | Pass | `supplier_profiles_plus` changes only native visibility. It does not modify qualification bytes, add rankings, or create a local entitlement toggle. |
| Async recovery model | Pass | Every terminal Premium state has explicit announcement text, recovery actions, and a useful focus target. Focus restoration occurs only after a user-triggered connect/purchase/restore/refresh action. |
| Responsive layout | Pass | Fixed hero typography was replaced by semantic `largeTitle`; input, action, RevenueCat, metadata, filter, and detail rows use horizontal-to-vertical `ViewThatFits` fallbacks. |
| Contrast/transparency response | Pass | Semantic card boundaries strengthen under Increase Contrast; decorative shadows/surfaces are reduced when Reduce Transparency is enabled. Textual state never relies on color alone. |

## Native contract checks (`automated`, current candidate passed)

The final verification command is:

```bash
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
# expected: NEXT_GEN_CHECKS_OK checks=15
```

The 15 checks cover:

1. Free/Premium portfolio projection.
2. Complete notice-level result preservation.
3. Empty notice sets.
4. Profile-count consistency.
5. Shared notice digest consistency.
6. Shared notice ordering.
7. Nested verdict totals.
8. Result/summary consistency.
9. Strict, bounded, deterministic workspace documents.
10. Strict notice import-preview decoding.
11. Search/buyer/deadline filters and stable lookup.
12. Stable identities across a synthetic 125-notice result set.
13. Terminal Premium announcement, recovery-action, and focus outcomes.
14. Fail-closed Test Store configuration.
15. Process-adapter deterministic byte preservation.

These checks validate contracts and pure state. They do not claim AppKit rendering quality, an
actual RevenueCat transaction, or VoiceOver speech.

The current 2026-08-05 Release packaging run also passed the embedded normalization and import
preview contracts twice with byte-identical output, ad-hoc signature verification, and app smoke
from outside the worktree. It produced the `.app`, zip, and SHA-256 companion on regenerable SSD
paths. Release is the no-key distributable and cannot substitute for the pending Debug Test Store
pass.

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

1. build or choose a validated workspace;
2. choose notices and inspect the import preview;
3. choose an explicit review point and run locally;
4. search/filter the complete free first-profile review queue;
5. opt into file-bookmark continuity only if useful;
6. understand or unlock Premium;
7. filter the shared comparison and open exact cell reasoning;
8. export deterministic JSON.

Accessibility-relevant code outcomes include distinct labels for secure configuration and file
actions, disabled-state preservation, combined profile summaries, native disclosures and links,
stable focus targets after Premium actions, VoiceOver announcements only when VoiceOver and a
visible app window are present, flexible row layouts, and Increased Contrast/Reduced Transparency
adaptation. Announcement content contains no key, customer identifier, or tender data.

## Still required (`pending`)

1. Build a fresh Debug `.app` from the exact final revision and repeat the selected-file and Test
   Store flow. Re-run the already-passing Release build only if the source changes afterward.
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
