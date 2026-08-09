# Privacy and crop checklist

Scope: every source in `timeline.json`, the rendered silent MP4, and any future replacement capture.

## Current package review

- [x] Only committed synthetic/public-safe product fixtures are represented.
- [x] No RevenueCat API key or partial key is visible, stored in the manifest, or copied into this
  directory.
- [x] No Judge Access reviewer code is visible.
- [x] No RevenueCat App User ID, anonymous customer identifier, account email, dashboard, or account
  URL is visible.
- [x] No personal email, TU Graz identity, notification, menu-bar account item, Finder sidebar,
  terminal, shell path, or browser tab is visible.
- [x] No confidential tender, real buyer, real supplier, or private document title is visible.
- [x] Synthetic buyer/profile names are clearly generic (`Example ...`).
- [x] The Test Store purchase sheet exposes only development copy, the public product identifier,
  localized test price, and subscription period.
- [x] The current Judge Access crop retains the literal “No purchase was made” sentence.
- [x] Dated Test Store and relaunch captures are labeled **baseline**, not current-revision proof.
- [x] The current Judge Access capture is labeled current `cbe8b20` evidence.
- [x] No VoiceOver overlay or spoken-accessibility success claim is used for the current silent pass.
- [x] Callouts are separate rendered layers. Two sources arrived with `.png` names but JPEG payloads;
  they are stored with truthful `.jpg` names after lossless `jpegtran -copy none` metadata removal.
  Their decoded-pixel SHA-256 values match the originals exactly.
- [x] The MP4 has no audio stream, metadata attachment, subtitle stream, or embedded account data.

## Crop-by-shot checks

| Shot | Required keep | Required exclude |
|---:|---|---|
| 1 | Hero, Portfolio Signal, shared/profile/changed counts | Desktop and window surroundings |
| 2 | Workspace/notices labels, review date, analyzed status | Full local file paths and Finder panels |
| 3 | All three verdict labels and synthetic titles | Any unrelated lower window content |
| 4 | Free summary, queue/filter/export evidence | Locked Premium reasoning |
| 5 | Comparison heading, same notice, different outcomes | Any code/key entry field |
| 6 | “Test Store Purchase”, product ID, localized price, development copy | System status area and external account UI |
| 7 | Entitlement copy, three fixture reports, Restore | Cursor highlight if it obscures wording |
| 8 | Judge Access expiration, “No purchase was made”, Restore, comparison | Reviewer code field and any key source |
| 9 | Unlocked state and Restore control | VoiceOver overlay, account/window surroundings |
| 10 | Icon and approved boundary copy | Unverified public URL or submission status |

## Mandatory rerun after replacement footage

- [ ] Review the first, middle, and last frame of every replacement shot at original resolution.
- [ ] Scrub every transition frame; a one-frame notification or key is still a privacy failure.
- [ ] Verify the final public export with `ffprobe`, then inspect it while logged out before upload.
- [ ] If any crop removes a qualifier such as “Test Store”, “baseline”, or “No purchase”, reject the
  crop even if it looks cleaner.
