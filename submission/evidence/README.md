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
