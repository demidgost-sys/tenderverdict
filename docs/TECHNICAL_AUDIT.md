# Technical audit — 2026-08-09

## Outcome

The competition product path is technically ready for the remaining evidence and media work. No
release-blocking defect remains in the RevenueCat Test Store or Judge Access flow. This verdict is
limited to the Shipaton evaluation build; it is not approval for a notarized public consumer
release or production billing.

Audited product revision: `cbe8b2071996edc2621a16cc9d10ce1ada63766e`.

The owner required a silent pass. VoiceOver speech, audio playback, microphones, and generated
sound were not started. Accessibility verification therefore used the macOS accessibility tree,
keyboard input, source contracts, and the existing silent native checks.

## Findings closed

| Severity | Finding | Resolution |
|---|---|---|
| Medium | Restore after accelerated Test Store expiry could leave no purchasable package until relaunch | Inactive restore now reloads the exact current offering/package and returns locked with the localized price and enabled purchase action |
| Medium | Explicit refresh and foreground re-entry could use stale entitlement state | Both paths now request current `CustomerInfo`; the live granted entitlement unlocked without relaunch and remained active after foreground re-entry |
| Medium | Judge Access copy always promised the campaign cutoff even if RevenueCat supplied an earlier expiration | The effective expiration is bounded to the local cutoff, formatted in the user's calendar, and described as an expiration rather than an inclusive promise |
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
5. the final UI reported **RevenueCat Judge Access expires December 31, 2026. No purchase was
   made.**

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
   unchanged; it must not be shortened.
3. **Spoken accessibility evidence — optional:** run the VoiceOver sequence only when sound is
   acceptable.
4. **Submission — blocked/open:** the private field inventory is complete, but its required
   store-release attestation has no truthful Next Gen path. The final recorded/public video and
   exact-head logged-out link review also remain.

## Verdicts

- Shipaton technical/product gate: **Approve for media and submission preparation**.
- Public consumer release: **Block until signing/notarization, production billing, and external
  workflow validation are complete**.
