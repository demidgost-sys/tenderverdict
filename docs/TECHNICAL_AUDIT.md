# Technical audit — 2026-08-19

## Outcome

The competition product path and submitted entry are technically ready for judging. The final
logical remediation adds an exclusive UTC Judge cutoff with scheduled local relock, aligns Python
and Swift profile-name identity normalization, and removes stale blocked-submission copy. No
competition-blocking defect remains. This verdict is limited to the Shipaton evaluation build; it
is not approval for a notarized public consumer release or production billing.

Audited source product revision: `68180b817b99db265d7585be51aa699dd4e99597`.
Latest hands-on package revision: `cbe8b2071996edc2621a16cc9d10ce1ada63766e`.

The owner required a silent pass. VoiceOver speech, audio playback, microphones, and generated
sound were not started. Accessibility verification therefore used the macOS accessibility tree,
keyboard input, source contracts, and the existing silent native checks.

## Findings closed

| Severity | Finding | Resolution |
|---|---|---|
| Medium | Restore after accelerated Test Store expiry could leave no purchasable package until relaunch | Inactive restore now reloads the exact current offering/package and returns locked with the localized price and enabled purchase action |
| Medium | Explicit refresh and foreground re-entry could use stale entitlement state | Both paths now request current `CustomerInfo`; the live granted entitlement unlocked without relaunch and remained active after foreground re-entry |
| Medium | Judge Access could remain unlocked in a continuously active process after its effective expiry, and local-calendar formatting made the campaign date ambiguous | The controller now treats `2027-01-01T00:00:00Z` as an exclusive cutoff, displays the inclusive UTC date, schedules relock at the earlier effective expiration, and replaces/cancels that schedule with customer-state changes |
| Low | Python accepted compatibility-equivalent profile names that Swift rejected | Both runtimes now apply trim, Unicode NFKC compatibility normalization, and case folding, with shared ASCII/full-width/composed/compatibility regression cases |
| High | Public repository documents still described the already submitted entry as blocked or draft | Active status, roadmap, scorecard, video, evidence, and submission documents now agree on Submitted, store release false, and authenticated/logged-out readbacks |
| Medium | Project status still named superseded product and evidence revisions | Runbook, evidence ledger, project status, and this audit now point to the exact current product and artifacts |

## Live RevenueCat evidence

The exact clean Debug package was launched with a process-local Test Store key that is absent from
the bundle and repository. A RevenueCat Granted Entitlement for `supplier_profiles_plus` produced
all of the following without a purchase:

1. a forced-current refresh changed the existing locked screen to **Portfolio comparison ready**
   without relaunch;
2. **Restore access** preserved the promotional entitlement;
3. background/foreground re-entry preserved access;
4. a full process relaunch recovered access from current `CustomerInfo`;
5. the final hands-on UI reported the December 31 boundary and **No purchase was made**; current
   source clarifies the same campaign boundary as available through December 31, 2026 UTC.

The genuine current-revision screenshot is
`submission/evidence/unlocked-judge-access-2026-08-09.png` (1020×754, SHA-256
`7432611a953749f5c19ebc5a02e1092da564e43e574600308bc4cf26eb94c3c9`). It contains neither the
raw reviewer code nor the Test Store key.

## Build and security evidence

| Artifact | Result |
|---|---|
| Release | `dist/next-gen-release-cbe8b20/`; 53 MiB app, 18 MiB zip; SHA-256 `77b25f7a0468603d49a3d65458540e34c9490097b5795c92c4c02034616dfa2f` |
| Debug | `dist/next-gen-debug-cbe8b20/`; 63 MiB app, 22 MiB zip; SHA-256 `e1bedc2eba22ddd0ae7495062f4ddacb7a60a16839d4a48658b5481d926ca84b` |
| Provenance | Both manifests record exact clean revision `cbe8b20`, RevenueCat `5.83.0`, ad-hoc signature, `api_key_included=false`, and configuration-correct Test Store availability |
| Native contracts | 20/20 in Debug and 20/20 in Release |
| Security | Release scanner, source secret boundary, public-tree check, and configuration fail-closed contracts pass |

The SSD was not mounted during this final pass, so these small ignored artifacts remain under the
repository's normal `dist/` output instead of being copied or moved elsewhere. They are not
committed.

## Silent accessibility verification

- Visible interactive controls expose native roles and useful names, including file selectors,
  date input, export, filters, search fields, restore, and each comparison cell.
- Comparison-cell names include profile, notice, verdict, and the action to open details.
- Twelve Tab steps repeatedly reached both search fields; one intervening focus position was not
  exposed by the accessibility snapshot, so this is not claimed as a full spoken screen-reader
  pass.
- Invalid-code recovery focus and terminal-state announcements remain covered by native contracts
  and the earlier hands-on field-focus check.
- VoiceOver spoken success, cancellation, failure, and restore remain intentionally unverified
  because this audit was required to stay silent.

## Remaining technical risks

1. **Public distribution — block:** the app is arm64, ad-hoc signed, and not notarized; there is no
   trusted installer or production App Store billing configuration.
2. **Judge access through judging — pass:** judging ends October 13, so the safe date-only `Until`
   boundary is October 14. The existing December 31 grant already exceeds it and was left
   unchanged. Current source additionally enforces the exclusive UTC campaign cutoff and local
   relock at the earlier entitlement expiration.
3. **Spoken accessibility evidence — optional:** run the VoiceOver sequence only when sound is
   acceptable.
4. **Submission — pass:** every truthful private field was saved, including store release = false.
   After the organizer corrected the contradictory validation, final Submit succeeded; the
   authenticated `Submitted` view, public project page, owner-approved 1:49 captioned YouTube v2,
   and repository/video links were verified.

## Verdicts

- Shipaton technical/product gate: **Approve for the submitted judging entry**.
- Public consumer release: **Block until signing/notarization, production billing, and external
  workflow validation are complete**.
