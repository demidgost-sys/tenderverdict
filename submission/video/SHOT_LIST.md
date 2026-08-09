# Shot list — silent animatic and final-capture replacement

All crop coordinates in `timeline.json` use source-image pixels from the top-left corner. The
animatic uses hard cuts so its duration remains deterministic.

| # | Time | Dur. | Current animatic source | What must be readable | Final capture replacement |
|---:|---|---:|---|---|---|
| 1 | 00:00–00:10 | 10 s | Top of `submission/screenshot-1179x2556.png` | Hero, one feed, three profiles, changed outcomes | Slow scroll or static packaged-app hero after Reload guided example |
| 2 | 00:10–00:23 | 13 s | Input section of the current portrait render | Workspace, normalized notices, review date, analyzed count | Choose committed fixtures, pause on import preview, run locally; never show Finder sidebars or full paths |
| 3 | 00:23–00:38 | 15 s | First-profile area of the current portrait render | `1 / 1 / 1`, Open documents, Watch, Reject | Scroll the packaged app through the three cards and expand one “Why this verdict” disclosure |
| 4 | 00:38–00:52 | 14 s | Current Free summary crop | Complete first supplier review and export affordance | Filter once, reset, and point to Export; do not imply that Portfolio details are Free |
| 5 | 00:52–01:08 | 16 s | Comparison crop from current Judge Access capture | Same notice, three independent profile outcomes | Filter the comparison and open one cell; preserve the exact verdict and reasons |
| 6 | 01:08–01:14 | 6 s | `assets/test-store-purchase-sheet-baseline-2026-08-04.jpg` | “Test Store Purchase”, product, localized price, development-only copy | Optional: replace only with a new continuous Debug Test Store take if separately authorized |
| 7 | 01:14–01:23 | 9 s | `submission/evidence/unlocked-test-store-2026-08-04.png` | Entitlement active and all three fixture profiles visible | Keep as clearly dated baseline unless an exact-final purchase take exists |
| 8 | 01:23–01:31 | 8 s | Current `unlocked-judge-access-2026-08-09.png` | RevenueCat Judge Access, expiration, “No purchase was made”, Restore | Current genuine evidence; do not crop out the no-purchase sentence |
| 9 | 01:31–01:39 | 8 s | Dated relaunch baseline | Unlocked state after relaunch baseline | If replacing, capture quit/relaunch only after hiding all keys/codes and do not use VoiceOver |
| 10 | 01:39–01:49 | 10 s | `submission/icon-1024.png` | Evaluation-build boundary, Apache 2.0, local/synthetic, no production billing | Keep deterministic end card; add final public repo URL only after logged-out verification |

## Capture settings for replacement footage

- 1920×1080 timeline, 30 fps, macOS dark appearance unless a light shot materially improves
  legibility; keep one appearance within a continuous action.
- Record the app window only. Hide desktop, Dock, menu-bar extras, notifications, cursor telemetry,
  Finder sidebars, terminal, account pages, and RevenueCat dashboard.
- Use the committed synthetic fixtures and a neutral review date already represented in the app.
- Do not accelerate interaction beyond readable human speed. Tighten dead time with cuts outside
  the purchase/entitlement transition.
- If a new Test Store take is ever authorized, purchase sheet and resulting entitlement must remain
  one continuous segment. The current task does not authorize that take.
