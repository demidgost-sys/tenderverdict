# Next Gen UX and accessibility audit

- Audit date: 2026-08-04
- App surface: self-contained macOS `.app`, default 1020×900 window
- Data: committed three-profile synthetic workspace and three synthetic notices
- RevenueCat configuration: process-local Test Store key; no usable key retained in the app or repo

## Outcome

The main local product path is coherent and packaged: launch, select files, run, retain one Free
profile, export deterministic JSON, and recover from invalid input. The RevenueCat Test Store path
was also exercised hands-on through offering load, cancel, failure, retry, success, entitlement
unlock, relaunch refresh, and restore. These are sandbox outcomes, not a real payment.

## Flow health

| Step | Result | Evidence |
|---|---|---|
| Packaged launch without source tree | Pass | Embedded core loaded 3 profiles / 3 notices with no `TENDERVERDICT_WORKTREE` |
| Synthetic first run | Pass | Free card showed Example Austria Services: 1 open, 0 watch, 2 reject |
| Choose workspace | Pass | Native open panel accepted `portfolio-workspace.json` |
| Choose notices | Pass | Native open panel accepted `notices.json` |
| Run selected inputs | Pass | Source label changed to both selected files; report remained 3 / 3 |
| Export JSON | Pass | Native save panel wrote atomically; exported SHA-256 matched CLI stdout exactly |
| Invalid `as_of` | Pass | Specific error appeared and the previous valid report stayed visible/exportable |
| Missing RevenueCat key | Pass | Secure configuration UI shown; no SDK request initiated |
| Non-Test key | Pass | `appl_invalid_fixture` was rejected locally and cleared from the secure field |
| Test Store offering | Pass | Current monthly package loaded at localized `0,99 $`; product identifier matched the dashboard |
| Cancellation | Pass | Test Store cancellation message appeared and access stayed locked |
| Failure and retry | Pass | Simulated failure produced a recoverable error; retry returned to the locked offering state |
| Entitlement unlock | Pass | Success activated `supplier_profiles_plus` and revealed all three reports |
| Relaunch refresh | Pass | Process-local key had to be re-entered; the existing entitlement then returned without a second purchase |
| Restore | Pass | Native Restore access called `restorePurchases()` and kept all reports unlocked |
| Dashboard readback | Pass | Sandbox view showed the new subscription; anonymous customer identifier was not recorded |

## Visual audit

The existing native SwiftUI language was retained and refined rather than replaced. Repeated
`ANALYZE`, `FREE`, and `PREMIUM` labels were removed, the product name and primary message now lead
the page, and one indigo accent governs interactive and structural emphasis. File rows use native SF
Symbols, cards share a 20 pt radius and restrained tinted shadow, and verdict metrics use nested
12 pt semantic surfaces. Primary hierarchy remains explicit:

1. choose inputs;
2. run locally;
3. review the always-free first profile;
4. understand or unlock the Premium portfolio;
5. export deterministic JSON.

At the minimum 900 pt width, labels and actions fit without clipping. Long file names truncate in
the middle while their complete accessible label remains available. The vertical scroll keeps the
Premium section reachable at smaller window heights. Light and dark appearances were rendered from
the real SwiftUI view and visually compared. Both preserve text hierarchy, semantic verdict colors,
field boundaries, and disabled-control states.

The committed competition screenshot is rendered from the real SwiftUI view through an AppKit
hosting view. Its narrower logical canvas improves the required portrait composition, while the
footer anchors the tall format and the locked card lists the real synthetic profile names without
claiming entitlement access. It is exactly 1179×2556, contains no device frame or metadata chunks,
and depicts the honest missing-key state. It is not transaction evidence.

`submission/evidence/unlocked-test-store-2026-08-04.png` is a genuine 1020×754 capture from the
packaged Debug app after the Test Store entitlement activated. It shows the active entitlement,
Restore access, and three unlocked profile reports without exposing the secure field, key, or
customer identifier. It is supplemental transaction evidence, not a replacement for the required
1179×2556 portrait asset.

## Accessibility audit

Passes observed in the macOS accessibility tree:

- Workspace, notices, review point, run, demo, export, secure key, and connect controls have distinct
  names.
- Disabled buttons remain exposed with their disabled state.
- The secure field reports secure text rather than its value.
- Status and error messages include textual meaning and do not rely on color alone.
- Each profile exposes one combined label with its name and open/watch/reject counts.
- Locked profile-preview rows expose the profile name and whether it is included or Premium.
- Native open and save panels provide standard keyboard and assistive-technology behavior.
- Buttons use large native control sizing; clickable labels are not custom gesture-only views.
- Tab focus followed Workspace → Notices → Review point → Load example → Export → Restore and
  correctly skipped disabled Run portfolio.
- VoiceOver exposed Restore access as a native button; activating it with VoiceOver preserved the
  active entitlement. VoiceOver was switched off again after the pass.

Still required before claiming full accessibility:

- verify logical announcements for asynchronous RevenueCat success, cancellation, and failure;
- test Increase Contrast, Reduce Transparency, and a large system text setting;
- confirm the final video captions and Devpost image alt text.

## Accepted follow-ups

1. Verify VoiceOver announcements during the asynchronous cancel/failure/success dialogs.
2. Test Increase Contrast, Reduce Transparency, and a large system text setting.
3. Caption and visually inspect the public sub-two-minute demo.
