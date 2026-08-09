# Shipaton Next Gen runbook

This runbook turns the repository into a competition submission without upgrading unverified facts
into claims. The controlling evidence record is [SHIPATON_EVIDENCE.md](SHIPATON_EVIDENCE.md), and
current implementation and submission counts are tracked in
[PROJECT_STATUS.md](PROJECT_STATUS.md). The current code, package, RevenueCat, security, and silent
accessibility review is recorded in [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md).

## Official submission gates

The checked 2026 rules allow macOS and give qualifying Next Gen students a public-repository and
video route without a store release or paid developer account. They still require substantive use
of the RevenueCat SDK, an active-student/academic-email check, a public open-source repository, a
public demo video under two minutes, a 1024×1024 icon, and at least one 1179×2556 screenshot without
a device frame.

Two previously open interpretation gates now have written organizer answers:

- On 2026-08-05, Shipaton Manager Perttu confirmed that a RevenueCat Test Store-only purchase is
  acceptable for the Next Gen entry. Preserve the complete thread as submission evidence:
  [Test Store eligibility answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient).
- The Shipaton team also confirmed that a macOS app is eligible and is not disadvantaged merely for
  being a macOS submission:
  [macOS submission answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission).

These answers resolve the platform and Test Store interpretation gates. They do not replace the
remaining personal eligibility, public repository, media, final-revision, or Devpost form checks.
Do not broaden either answer into a promise about judging outcome.

The public Devpost page currently lists Charlie Chapman and David Barnard as judges, while the
Official Rules allow the panel to change. Product prioritization therefore follows the published
problem, working-app, RevenueCat/monetization, and product/technical-care criteria recorded in the
[competition scorecard](COMPETITION_SCORECARD.md), not inferred personal preferences.

Sources rechecked on 2026-08-05:

- [Official Rules](https://revenuecat-shipaton-2026.devpost.com/rules)
- [Next Gen Award](https://www.shipaton.com/next-gen)
- [FAQ](https://www.shipaton.com/faq)
- [RevenueCat Test Store](https://www.revenuecat.com/docs/test-and-launch/sandbox/test-store)
- [RevenueCat macOS installation](https://www.revenuecat.com/docs/getting-started/installation/macos)
- [Test Store eligibility answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient)
- [macOS submission answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission)

The owner has joined with the qualifying student profile, and the authenticated private-field
inventory is complete. The draft overview, evidence-bounded story, repository link, tags, and three
verified gallery images were saved and read back; Additional info remains unsaved. Its required
store-release checkbox has no No option or visible Next Gen exception, so it cannot be checked
truthfully for this store-exempt macOS entry. A narrow field-specific follow-up is pending in the
[public organizer thread](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient).
Do not treat the earlier Test Store answer as an answer to this different form-attestation issue,
and do not accept Terms or submit without a separate final action.

## Current product proof

The current source adds a complete local Portfolio Workspace journey on top of the deterministic
Python contracts:

1. Create, reorder, and validate one to five supplier profiles in the native Profile Builder.
2. Choose normalized CSV or JSON notices and inspect their count, first records, and metadata gaps
   before running anything.
3. Optionally remember only security-scoped bookmarks for the two chosen files. Tender contents,
   reports, review dates, and the RevenueCat key remain session-only; restoring those files never
   runs the selected portfolio automatically.
4. Run one bounded notice set through the canonical core and keep the first complete report and
   export free.
5. Search and filter the review queue by text, buyer, deadline presence, and verdict.
6. Unlock the full comparison through `supplier_profiles_plus`, then open any comparison cell to
   inspect that exact profile/notice verdict, reasons, unknowns, next step, and safe HTTPS source.

The native contract suite covers strict/deterministic workspace documents, schema-3 Free export,
visible control/bidi text, import previews, large-list filtering with stable identities,
process-byte equality, pure terminal RevenueCat announcement/recovery/focus outcomes, exact
dashboard identifiers, Debug/Release fail-closed configuration, and the existing
portfolio/provenance invariants. Exact current totals live in
[project status](PROJECT_STATUS.md).

## Reproducible local build

Use macOS, Swift 6, Python 3.11+, and the pinned build requirements:

```bash
python3 -m venv .venv-build
.venv-build/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r requirements-desktop-build.txt
.venv-build/bin/python tools/build_next_gen.py
```

The builder creates:

- `dist/next-gen/TenderVerdictNextGen.app`;
- `dist/next-gen/TenderVerdictNextGen-macos.zip`;
- `dist/next-gen/TenderVerdictNextGen-macos.sha256`.

It builds the release Swift executable, freezes a portfolio-only Python core, copies fixtures and
licenses, embeds Swift package resources, ad-hoc signs the app, runs the app smoke test from `/`
without a worktree, archives it, and writes a checksum. The bundle is not notarized.

The fresh Release and Debug builds from exact clean product revision
`cbe8b2071996edc2621a16cc9d10ce1ada63766e` passed 20 configuration-specific native checks,
embedded smoke, ad-hoc signature verification, checksum creation, and worktree-independent app
smoke. Release intentionally rejects Test Store configuration. The SSD was not mounted during this
pass, so the small ignored outputs remain under `dist/next-gen-release-cbe8b20/` and
`dist/next-gen-debug-cbe8b20/`; they were not copied, moved, or committed.

After any native source or asset change, regenerate all three outputs rather than presenting the
older bundle as the current candidate. If build scratch must live on a separate volume, use the
documented flags rather than moving the repository or toolchain:

```bash
.venv-build/bin/python tools/build_next_gen.py \
  --build-root /absolute/regenerable/build-root \
  --swift-scratch-path /absolute/regenerable/swift-scratch
```

## RevenueCat dashboard contract

Configured and hands-on verified on 2026-08-04:

| Object | Identifier / choice |
|---|---|
| Project/app | TenderVerdict Next Gen macOS |
| Store | RevenueCat Test Store |
| Entitlement | `supplier_profiles_plus` |
| Product | `supplier_profiles_plus_monthly`, monthly, USD 0.99 |
| Offering | Current `supplier_profiles_plus` offering with one `$rc_monthly` package |
| SDK | Apple Purchases `5.83.0` |

Do not put a key in Git, a scheme committed to Git, screenshots, terminal logs, or Devpost text.
Paste the `test_` key into the secure in-app field for the current launch. RevenueCat rejects Test
Store keys in Release builds by design, so run the hands-on transaction sequence from a separately
packaged Debug build:

```bash
.venv-build/bin/python tools/build_next_gen.py \
  --configuration debug \
  --output-dir dist/next-gen-debug \
  --build-root build/next-gen-debug
```

Keep the ordinary Release build as the no-key distributable artifact. Neither bundle may contain a
usable API key.

## Required transaction evidence

Record one continuous hands-on sequence on the freshly packaged Debug app:

1. No key: app is locked and makes no RevenueCat request.
2. Invalid non-Test key: rejected locally.
3. Valid Test Store key: current offering and localized price load.
4. Cancel outcome: access stays locked.
5. Failure outcome: clear retry state appears.
6. Success outcome: `CustomerInfo` activates `supplier_profiles_plus` and all reports appear.
7. Relaunch, foreground re-entry, or refresh: current active access returns.
8. Immediate restore: access returns through `restorePurchases()`.
9. Expiry recovery: after the accelerated subscription becomes inactive, choose **Restore access**
   and verify the app returns to locked with the localized exact monthly package and an enabled
   purchase action without relaunching.
10. RevenueCat dashboard: the same customer and Test Store event are visible.

Capture dates, app revision, SDK version, entitlement identifier, and outcome. Do not claim a real
payment or App Store transaction.

The 2026-08-04 packaged Debug baseline completed all nine steps. The current offering loaded at a
localized `0,99 $`; cancel and failure stayed locked; retry recovered; success activated
`supplier_profiles_plus`; relaunch with process-local key re-entry recovered the entitlement;
Restore access invoked `restorePurchases()`; and RevenueCat showed the sandbox subscription. The
key and anonymous customer identifier were not retained. VoiceOver exposed and activated Restore,
and was switched off again after the pass.

The fresh `3cf20ed` Debug package repeated the current offering, cancellation, simulated failure,
retry, valid purchase, immediate restore, and relaunch refresh outcomes. Its manifest records a
clean Debug source revision, Test Store enabled, RevenueCat `5.83.0`, and no bundled key. The key was
cleared after the run. A later restore after the accelerated Test Store subscription expired
correctly returned locked; immediate restore remained unlocked. The current pass also covered
keyboard navigation, Increase Contrast, Reduce Transparency, and a temporary large-text renderer
override that was reverted immediately. It did not re-open the dashboard and did not run VoiceOver.
Manual VoiceOver verification of asynchronous success, cancellation, and failure remains
unverified and is an optional accessibility follow-up, not a submission gate.

The exact clean `cbe8b20` Debug package then verified the no-purchase Judge Access path. A
forced-current refresh changed the already-open locked screen to the Premium comparison without
relaunch; Restore, background/foreground re-entry, and full process relaunch preserved access. The
UI reports the RevenueCat expiration date as **December 31, 2026** and explicitly states that no
purchase was made. The exact-revision unlocked screenshot is stored at
`submission/evidence/unlocked-judge-access-2026-08-09.png`.

The final silent `217c091` Debug receipt supersedes the runtime matrix without replacing that
genuine screenshot. It repeats missing/invalid key, offering, cancel, simulated failure, retry,
Test Store success, immediate Restore, foreground, relaunch, natural accelerated-expiry
locked/offering recovery, Judge refresh/Restore/foreground/relaunch, and an independent check of
the unmodified checksummed archive. The key remained process-local, the existing December 31 grant
was not changed, and no real payment occurred. Exact artifact metadata and the complete bounded
matrix live in `submission/evidence/README.md`.

## Hackathon Judge Access

Judge Access is a separate no-purchase evaluation route backed by RevenueCat Granted Entitlements,
not an Apple offer code and not a local Premium override. Keep the raw code list outside Git and do
not include it in public screenshots or repository text.

For each assigned reviewer slot:

1. Launch the fresh Debug evaluation app with the process-local Test Store key and activate its
   assigned Judge Access code once, creating the dedicated RevenueCat App User ID.
2. Find that customer in RevenueCat and grant `supplier_profiles_plus` for the required review
   window. RevenueCat's date-only **Until date** is an expiration boundary, not an inclusive
   end-of-day promise. If access must remain available through all of December 31, select January
   1, 2027 in the dashboard; the app still rejects known Judge Access identities after its local
   **2026-12-31 23:59:59 UTC** cutoff. Granted Entitlements create no purchase and do not affect
   billing.
3. Activate the same code again and verify the app identifies the RevenueCat promotional grant,
   states that no purchase was made, and exposes the Premium workspace.
4. Refresh, background/foreground, and relaunch with key re-entry; verify access remains governed by
   current `CustomerInfo`.
5. Exercise an invalid code and confirm the field receives recovery focus without changing the
   RevenueCat identity or unlocking Premium.

The app also rejects known Judge Access identities after December 31, 2026. Dashboard expiry and
the local cutoff must agree; neither one should be described as a paid subscription or real store
transaction.

## Submission assets

The repository contains:

- `submission/icon-1024.png` — canonical reviewed icon at exactly 1024×1024;
- `submission/screenshot-1179x2556.png` — current pre-transaction screenshot at exactly
  1179×2556, regenerated, sanitized, and visually reviewed in light and dark appearance;
- `submission/evidence/unlocked-test-store-2026-08-04.png` — genuine 1020×754 supplemental unlocked
  baseline, not a replacement for the required portrait screenshot or fresh-build evidence;
- `submission/evidence/unlocked-judge-access-2026-08-09.png` — genuine 1020×754 current-revision
  Judge Access capture after refresh, Restore, foreground, and relaunch, with no code or key;
- `submission/evidence/voiceover-restore-2026-08-04.png` — baseline assistive-technology evidence;
- [a timed demo script](DEMO_SCRIPT.md);
- [a Devpost draft](../submission/devpost-draft.md).

Regenerate the portrait image after building the current revision:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --render-submission-screenshot \
  "$PWD/submission/screenshot-1179x2556.png"
python3 tools/prepare_submission_assets.py
```

The final entry may use the exact portrait screenshot plus a genuine unlocked supplemental capture.
Never use a fake entitlement state as evidence.

## Final checklist

- [x] Shipaton Manager Perttu confirmed the Test Store-only purchase path on 2026-08-05.
- [x] Shipaton confirmed that macOS is eligible and carries no platform-only disadvantage.
- [x] Devpost participation uses a TU Graz academic-domain email and the owner confirmed current
  student status, TU Graz affiliation, and July 2028 graduation on 2026-08-05.
- [x] Exact private Devpost fields are inspected after joining; the saved overview, story,
  repository link, tags, and three gallery images were read back without exposing private values.
- [ ] The required store-release attestation has a truthful Next Gen path through a form correction
  or written field-specific organizer instruction.
- [x] Public draft branch contains source, instructions, assets, and Apache-2.0 license.
- [x] The release-configuration artifact named in project status passes checksum creation,
  signature, embedded-core contract/determinism, configuration-specific native checks, and
  worktree-independent smoke checks.
- [x] A fresh Debug package is generated from the final product revision for the hands-on Test Store pass.
- [x] The current candidate passes the complete source/package gate recorded in
  [project status](PROJECT_STATUS.md), including Python, Debug/Release native, formatting, typing,
  public-tree, security, asset, and diff checks.
- [x] The current pushed candidate passes its exact-head PR CI checks.
- [x] The exact clean `217c091` Debug package repeats missing/invalid key, offering, cancel,
  simulated failure, retry, Test Store success, immediate Restore, foreground, relaunch, natural
  accelerated-expiry locked/offering recovery, and makes no real payment.
- [x] Current Judge Access grant survives refresh, Restore, foreground, full relaunch, and a check
  of the unmodified checksummed `217c091` archive bundle; the existing December 31 grant was not
  changed.
- [x] Current large-text, Increase Contrast, and Reduce Transparency views are manually checked;
  light/dark and the regenerated portrait screenshot also pass visual review.
- [x] The link-accessible YouTube demo is 1:49, shows the packaged macOS app, includes burned and
  selectable English captions, and passes logged-out URL plus YouTube policy checks.
- [ ] The owner completes one normal-speed watch/listen of the hosted demo.
- [x] Icon is exactly 1024×1024.
- [x] At least one current screenshot is exactly 1179×2556 and has no device frame.
- [x] Devpost draft contains no key, private data, unsupported payment claim, or fabricated result.
- [x] The current pushed SHA, public repository, and video URL are recorded and checked without
  authenticated browser state.
- [ ] The final submitted entry and submitted view are checked while logged out.

## Optional evidence follow-ups

- [ ] VoiceOver announces asynchronous success, cancellation, and failure and restores useful
  focus. Until checked, describe the routing as implemented and contract-tested, not hands-on
  spoken evidence.
- [ ] RevenueCat dashboard readback is refreshed during a later continuous Test Store take; the
  existing dashboard proof remains the dated 2026-08-04 baseline.
- [ ] Independent opt-in workflow sessions are run only if future product validation is useful;
  no user-value or adoption result is currently claimed.
