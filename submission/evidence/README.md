# Local Test Store evidence

Captured on 2026-08-04 from the reproducibly packaged Debug macOS app using RevenueCat Apple SDK
`5.83.0` and entitlement `supplier_profiles_plus`.

- `unlocked-test-store-2026-08-04.png` shows the genuine active entitlement, native Restore access
  action, and all three synthetic profile reports.
- `voiceover-restore-2026-08-04.png` shows VoiceOver enabled with Restore access focused before it
  was activated through the VoiceOver command.
- `unlocked-judge-access-2026-08-09.png` shows exact clean product revision `cbe8b20` after the
  RevenueCat grant unlocked through a forced-current refresh and then survived Restore,
  background/foreground re-entry, and full relaunch. It states that no purchase was made.

The Test Store key was supplied only to the process. None of the images contains the key, a raw
reviewer code, RevenueCat customer identifier, account UI, real notice data, or a real-payment
claim. The images are supplemental local evidence; the canonical Devpost-size image remains
`submission/screenshot-1179x2556.png`.

## Final RevenueCat QA receipt — 2026-08-09

This public-safe receipt combines `automated` package evidence and silent `manual` runtime evidence
for repository revision `217c091d21d7b997f1271abc7e263e49e6de8478`. It contains no API key,
reviewer code, RevenueCat customer identifier, email address, account URL, or private/local path.

### Candidate and official access window

| Fact | Evidence |
|---|---|
| Debug archive | `TenderVerdictNextGen-macos.zip`, 21,793,093 bytes |
| Archive SHA-256 | `ee1e30696deb5f322c81d8bdfd2e6b871d5467a7bc4a53f6dac7f12ab76f0f7a` |
| Build manifest | `version=0.2.0a1`, `source_dirty=false`, `build_configuration=debug`, `test_store_enabled=true`, RevenueCat `5.83.0`, entitlement `supplier_profiles_plus`, embedded offline Python, `api_key_included=false` |
| Trust boundary | arm64, valid ad-hoc signature, no Team ID, not notarized; local evaluation artifact rather than a public consumer release |
| Submission deadline | September 30, 2026 at 23:45 PDT, from the [Shipaton Official Rules](https://revenuecat-shipaton-2026.devpost.com/rules) |
| Judging window | October 1, 2026 at 00:00 PDT through October 13, 2026 at 12:00 PDT; the same Rules require free, unrestricted testing until judging ends |
| Safe RevenueCat `Until` boundary | October 14, 2026, using the next calendar day so access cannot expire during the final judging day |
| Existing Judge grant | `Until` December 31, 2026, confirmed through forced-current RevenueCat `CustomerInfo` and truthful in-app expiry copy; this already exceeds the safe boundary and was left unchanged |

### Outcome matrix

| Check | Outcome | Evidence |
|---|---|---|
| Clean Debug package | `PASS` | Exact clean revision built with 20 Debug-native checks, embedded smoke, signature verification, ZIP creation, and checksum verification |
| Complete local source gate | `PASS` | 125 Python tests; 20 Debug and 20 Release native checks; Ruff check/format; Mypy; Swift format; public-tree; security scan; source smoke; wheel/sdist and package smoke; diff check |
| Missing key | `PASS_LOCKED` | No RevenueCat request path became available and Connect remained disabled |
| Invalid key | `PASS_LOCAL_REJECTION` | Non-Test input was rejected locally, cleared, and did not connect |
| Offering | `PASS` | Expected monthly Test Store package loaded at localized `0,99 $`; the UI stated that no real charge would occur |
| Cancel | `PASS_LOCKED` | Cancellation kept access locked and reported that access was unchanged |
| Simulated failure | `PASS_LOCKED` | Failure produced the bounded retry state without entitlement access |
| Retry | `PASS_RECOVERED` | Retry reloaded the expected locked offering |
| Simulated Test Store success | `PASS_PREMIUM` | Test Store `CustomerInfo` activated `supplier_profiles_plus` and revealed the three-profile comparison; this was sandbox simulation, not a real payment |
| Immediate Restore | `PASS_PREMIUM` | Restore preserved active Test Store access without another simulated purchase |
| Foreground refresh | `PASS_PREMIUM` | Background/foreground re-entry preserved active access |
| Full relaunch | `PASS_PREMIUM` | Re-entering the process-local Test Store key recovered the same entitlement without another simulated purchase |
| Accelerated expiry | `PASS_LOCKED_RECOVERED_OFFERING` | A forced refresh shortly after the documented 25-minute total still reported active access; a refresh shortly after 30 minutes returned locked and immediately reloaded the expected offering |
| Judge activation/refresh | `PASS_PREMIUM` | The existing grant produced `RevenueCat Judge Access expires December 31, 2026` and `No purchase was made` |
| Judge Restore | `PASS_PREMIUM` | Restore preserved granted access and the same expiry/no-purchase copy |
| Judge foreground | `PASS_PREMIUM` | Background/foreground re-entry preserved granted access |
| Judge full relaunch | `PASS_PREMIUM` | A new process plus forced-current refresh recovered the existing grant and truthful expiry/no-purchase copy |
| Unmodified archive bundle | `PASS_PREMIUM` | The app directly from the checksummed archive independently recovered the same Judge entitlement after process-local configuration |
| Audio boundary | `PASS_SILENT` | VoiceOver, TTS, microphone, sound playback, and audio files were not launched |

RevenueCat documents a 25-minute total for a one-month Test Store subscription after accelerated
renewals in [Test Store subscription renewals and expiration](https://www.revenuecat.com/docs/test-and-launch/sandbox/test-store#subscription-renewals-and-expiration).
The later live expiry is recorded as server-timing variance, not as a product defect or a broader
timing guarantee.

No real payment, production purchase, or grant/dashboard mutation occurred in this receipt. A
later final-integration pass pushed the public-safe evidence, completed exact-head CI, and created a
link-accessible captioned YouTube demo saved in the Devpost draft. The owner listening pass, the
truthful private-form resolution, and final Devpost submission remain separate gates. VoiceOver
behavior is deliberately not claimed by this silent receipt.
