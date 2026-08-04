# Shipaton submission assets

This directory contains public, synthetic-only entry materials. It must never contain a RevenueCat
key, account screenshot, private identifier, confidential notice, or unsupported transaction claim.

| Asset | Status | Contract |
|---|---|---|
| `icon-1024.png` | Ready | Exactly 1024×1024, extracted byte-for-byte from the reviewed ICNS 1024px chunk |
| `screenshot-1179x2556.png` | Ready as pre-transaction candidate | Exactly 1179×2556, real SwiftUI view, missing-key state, no device frame or metadata chunks |
| `evidence/unlocked-test-store-2026-08-04.png` | Ready as supplemental evidence | Genuine 1020×754 packaged Debug app after Test Store unlock; no key or customer identifier |
| `evidence/voiceover-restore-2026-08-04.png` | Ready as local accessibility evidence | VoiceOver enabled with native Restore access focus; not a Devpost-size asset |
| Public video | Pending | Public YouTube/Vimeo, under two minutes, packaged macOS app |
| `devpost-draft.md` | Ready with explicit placeholders | Remove blockers/placeholders only after evidence exists |

Regenerate both committed images:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --render-submission-screenshot \
  "$PWD/submission/screenshot-1179x2556.png"
python3 tools/prepare_submission_assets.py
python3 tools/check_public_tree.py
```

The sanitizer removes ancillary PNG metadata chunks without changing `IHDR`, `IDAT`, or `IEND`
image data. The public-tree gate verifies exact dimensions and PNG structure.

For the final entry, use the exact portrait screenshot and, if the form permits multiple images,
supplement it with the genuine unlocked Test Store capture. Do not use a hidden launch flag, edited
entitlement, mock purchase, or composited fake as transaction evidence.
