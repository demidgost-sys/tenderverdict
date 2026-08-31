# Shipaton demo script

The canonical production package is [`submission/video/`](../submission/video/README.md). Its
machine-checked timeline ends at **1:49**, one second below the working 1:50 ceiling and eleven
seconds below the official two-minute limit.

Use these owning files instead of copying the script here:

- [beat sheet](../submission/video/BEAT_SHEET.md);
- [shot list](../submission/video/SHOT_LIST.md);
- [canonical English narration](../submission/video/narration-en.txt);
- [captions](../submission/video/captions-en.srt);
- [claim and asset manifest](../submission/video/ASSET_MANIFEST.md);
- [Russian director handoff](../submission/video/DIRECTOR_HANDOFF_RU.md).

The checked silent MP4 is an ignored local handoff artifact, not a tracked public file or a public
demo. Its SHA-256, stream layout, and exact runtime are recorded in the committed public-safe QA
receipt; the companion ignored local receipt also records its absolute path.

## Capture setup

- Build the exact final revision with `--configuration debug`; Test Store purchases do not run in
  the ordinary Release package.
- Record only after the full verification emits its `NEXT_GEN_CHECKS_OK` completion marker in both
  Debug and Release on that final revision; use [project status](PROJECT_STATUS.md) for the expected
  current total.
- Prepare the selected synthetic files and a valid `test_` key before capture. Connect the offering
  without showing the key, terminal, account email, or RevenueCat dashboard secrets.
- Keep the RevenueCat purchase sheet and resulting entitlement state in one continuous segment.
  Cuts may tighten navigation elsewhere, but must not hide a failure or fabricate state.
- If the Test Store sheet or Restore exceeds the budget, shorten the Profile Builder and filter
  pauses first. Keep the final published video **at or below 1:50** and the official under-two-minute
  limit.
- State **Test Store, no real charge**. Do not call it an App Store payment.
- Avoid calling verdicts legal decisions, recommendations, AI predictions, scores, or rankings.
- Use the package captions without rewriting them, then check the final public YouTube/Vimeo cut at
  normal speed with sound before entering its URL in Devpost.
