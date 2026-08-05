# Shipaton Next Gen runbook

This runbook turns the repository into a competition submission without upgrading unverified facts
into claims. The controlling evidence record is [SHIPATON_EVIDENCE.md](SHIPATON_EVIDENCE.md), and
current implementation and submission counts are tracked in
[PROJECT_STATUS.md](PROJECT_STATUS.md).

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

The owner has joined with the qualifying student profile. Project creation was opened but stopped
at visual reCAPTCHA before a draft or private fields existed. Do not invent its fields: after the
owner completes that visual challenge, inspect them while signed in and do not submit without a
separate final action.

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

The fresh 2026-08-05 Release build from the current source passed embedded workspace normalization
and notice inspection twice with byte-identical output, contract decoding, ad-hoc signature
verification, and a worktree-independent app smoke test. The `.app`, zip, and SHA-256 companion
were created on regenerable SSD build/output paths. A separate clean Debug artifact from
`3cf20ed0d1607b7feb943109f72c1c528df55e5b` was then built on the SSD for transaction evidence;
Release intentionally continues to reject Test Store transactions.

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
7. Relaunch or refresh: active access returns.
8. Restore: access returns through `restorePurchases()`.
9. RevenueCat dashboard: the same anonymous customer and Test Store event are visible.

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
Manual VoiceOver verification of asynchronous success, cancellation, and failure remains pending.

## Submission assets

The repository contains:

- `submission/icon-1024.png` — canonical reviewed icon at exactly 1024×1024;
- `submission/screenshot-1179x2556.png` — current pre-transaction screenshot at exactly
  1179×2556, regenerated, sanitized, and visually reviewed in light and dark appearance;
- `submission/evidence/unlocked-test-store-2026-08-04.png` — genuine 1020×754 supplemental unlocked
  baseline, not a replacement for the required portrait screenshot or fresh-build evidence;
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
- [ ] Exact private Devpost fields are inspected after joining; required claims and assets agree
  with the final repository state.
- [x] Public draft branch contains source, instructions, assets, and Apache-2.0 license.
- [x] The release-configuration artifact named in project status passes checksum creation,
  signature, embedded-core contract/determinism, configuration-specific native checks, and
  worktree-independent smoke checks.
- [x] A fresh Debug package is generated from the final product revision for the hands-on Test Store pass.
- [x] The current candidate passes the complete source/package gate recorded in
  [project status](PROJECT_STATUS.md), including Python, Debug/Release native, formatting, typing,
  public-tree, security, asset, and diff checks.
- [ ] The exact final submitted revision passes its pushed PR CI checks.
- [x] Test Store success, cancel, failure, retry, relaunch, and immediate restore are refreshed on
  the final product Debug package.
- [ ] RevenueCat dashboard readback is refreshed for the same final evidence take; the existing
  dashboard proof remains the dated 2026-08-04 baseline.
- [ ] VoiceOver announces asynchronous success, cancellation, and failure and restores useful focus.
- [x] Current large-text, Increase Contrast, and Reduce Transparency views are manually checked;
  light/dark and the regenerated portrait screenshot also pass visual review.
- [ ] Public YouTube or Vimeo demo is under two minutes and shows the packaged app on macOS.
- [x] Icon is exactly 1024×1024.
- [x] At least one current screenshot is exactly 1179×2556 and has no device frame.
- [x] Devpost draft contains no key, private data, unsupported payment claim, or fabricated result.
- [ ] Repository URL, video URL, and final commit SHA are entered and checked in a logged-out view.
