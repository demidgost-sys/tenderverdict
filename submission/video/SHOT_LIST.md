# Shot list — silent animatic and final-capture replacement

All crop coordinates in `timeline.json` use source-image pixels from the top-left corner. The
animatic uses hard cuts so its duration remains deterministic.

| # | Time | Dur. | Current animatic source | What must be readable | Final capture replacement |
|---:|---|---:|---|---|---|
| 1 | 00:00–00:09.5 | 9.5 s | Top of `submission/screenshot-1179x2556.png` | Hero, one feed, three profiles, changed outcomes | Captured from the exact Release app window after Reload guided example |
| 2 | 00:09.5–00:22 | 12.5 s | Input section of the current portrait render | Workspace, normalized notices, review date, analyzed count | Captured from the exact Release app window; no Finder sidebar or full path visible |
| 3 | 00:22–00:36 | 14 s | First-profile area of the current portrait render | `1 / 1 / 1`, Open documents, Watch, Reject | Captured scrolling through the queue and expanding “Why this verdict” |
| 4 | 00:36–00:48 | 12 s | Current Free summary crop | Complete first supplier review and export affordance | Captured Watch filtering, reset, and portfolio scroll |
| 5 | 00:48–01:04 | 16 s | Comparison crop from current Judge Access capture | Same notice, three independent profile outcomes | Genuine sanitized still; preserve exact verdict and reasons |
| 6 | 01:04–01:11.2 | 7.2 s | `assets/test-store-purchase-sheet-baseline-2026-08-04.jpg` | “Test Store Purchase”, product, localized price, development-only copy | Keep dated baseline; no new purchase was performed |
| 7 | 01:11.2–01:19.7 | 8.5 s | `submission/evidence/unlocked-test-store-2026-08-04.png` | Entitlement active and all three fixture profiles visible | Keep clearly dated baseline; no exact-final purchase claim |
| 8 | 01:19.7–01:27.1 | 7.4 s | Current `unlocked-judge-access-2026-08-09.png` | RevenueCat Judge Access, expiration, “No purchase was made”, Restore | Genuine evidence; do not crop out the no-purchase sentence |
| 9 | 01:27.1–01:35.7 | 8.6 s | Dated relaunch baseline | Unlocked state after relaunch baseline | Audit-scoped baseline; no key/code shown |
| 10 | 01:35.7–01:49 | 13.3 s | `submission/icon-1024.png` | Synthetic data, no usable key, no production billing, Apache 2.0 | Deterministic end card; no public URL added before logged-out QA |

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
