# Shipaton Next Gen runbook

This runbook turns the repository into a competition submission without upgrading unverified facts
into claims. The controlling evidence record is [SHIPATON_EVIDENCE.md](SHIPATON_EVIDENCE.md).

## Official submission gates

The checked 2026 rules allow macOS and give qualifying Next Gen students a public-repository and
video route without a store release or paid developer account. They still require substantive use
of the RevenueCat SDK, an active-student/academic-email check, a public open-source repository, a
public demo video under two minutes, a 1024×1024 icon, and at least one 1179×2556 screenshot without
a device frame.

Sources rechecked on 2026-08-04:

- [Official Rules](https://revenuecat-shipaton-2026.devpost.com/rules)
- [Next Gen Award](https://www.shipaton.com/next-gen)
- [FAQ](https://www.shipaton.com/faq)
- [RevenueCat Test Store](https://www.revenuecat.com/docs/test-and-launch/sandbox/test-store)
- [RevenueCat macOS installation](https://www.revenuecat.com/docs/getting-started/installation/macos)

No checked Shipaton source explicitly resolves whether a Test Store-only purchase satisfies the
purchase requirement. The owner has directed work to continue without waiting for a response, so
retain this as a disclosed eligibility risk and do not describe it as organizer approval.

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
Paste the `test_` key into the secure in-app field for the current launch.
RevenueCat rejects Test Store keys in Release builds by design, so run the hands-on transaction
sequence from a separately packaged Debug build:

```bash
.venv-build/bin/python tools/build_next_gen.py \
  --configuration debug \
  --output-dir dist/next-gen-debug \
  --build-root build/next-gen-debug
```

Keep the ordinary Release build as the no-key distributable artifact. Neither bundle may contain a
usable API key.

## Required transaction evidence

Record one continuous hands-on sequence on the packaged app:

1. No key: app is locked and makes no RevenueCat request.
2. Invalid non-Test key: rejected locally.
3. Valid Test Store key: current offering and localized price load.
4. Cancel outcome: access stays locked.
5. Failure outcome: clear retry state appears.
6. Success outcome: `CustomerInfo` activates `supplier_profiles_plus` and all three reports appear.
7. Relaunch or refresh: active access returns.
8. Restore: access returns through `restorePurchases()`.
9. RevenueCat dashboard: the same anonymous customer and Test Store event are visible.

Capture dates, app revision, SDK version, entitlement identifier, and outcome. Do not claim a real
payment or App Store transaction.

The 2026-08-04 packaged Debug pass completed all nine steps. The current offering loaded at a
localized `0,99 $`; cancel and failure stayed locked; retry recovered; success activated
`supplier_profiles_plus`; relaunch with process-local key re-entry recovered the entitlement;
Restore access invoked `restorePurchases()`; and RevenueCat showed the sandbox subscription. The
key and anonymous customer identifier were not retained. VoiceOver exposed and activated Restore,
and was switched off again after the pass.

## Submission assets

The repository already contains:

- `submission/icon-1024.png` — canonical reviewed icon at exactly 1024×1024;
- `submission/screenshot-1179x2556.png` — honest pre-transaction app state at exactly 1179×2556;
- `submission/evidence/unlocked-test-store-2026-08-04.png` — genuine 1020×754 supplemental unlocked
  state, not a replacement for the required portrait screenshot;
- `submission/evidence/voiceover-restore-2026-08-04.png` — local assistive-technology pass showing
  Restore focus with VoiceOver enabled;
- [a timed demo script](DEMO_SCRIPT.md);
- [a Devpost draft](../submission/devpost-draft.md).

Regenerate the image assets with:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --render-submission-screenshot \
  "$PWD/submission/screenshot-1179x2556.png"
python3 tools/prepare_submission_assets.py
```

The final submission may use the exact portrait screenshot plus the genuine unlocked supplemental
capture. Never use a fake entitlement state as evidence.

## Final checklist

- [ ] Either a written organizer answer permits the Test Store-only path or the unresolved risk is
  disclosed without claiming approval.
- [ ] Devpost participation uses the qualifying academic email and student status is current.
- [ ] Public branch contains all source, assets, instructions, and the Apache-2.0 license.
- [ ] CI passes on the submitted revision.
- [x] Packaged `.app` checksum, signature, smoke test, and hands-on local-file flow pass.
- [x] Test Store success, cancel, failure, retry, relaunch, restore, and dashboard evidence is
  recorded locally.
- [ ] Public YouTube or Vimeo demo is under two minutes and shows the app on macOS.
- [x] Icon is exactly 1024×1024.
- [x] At least one screenshot is exactly 1179×2556 and has no device frame.
- [x] Devpost draft contains no key, private data, unsupported eligibility claim, or real-payment
  claim.
- [ ] Repository URL, video URL, and final commit SHA are entered and checked in a logged-out view.
