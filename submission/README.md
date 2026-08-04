# Shipaton submission assets

This directory contains public, synthetic-only entry materials. It must never contain a RevenueCat
key, account screenshot, private identifier, confidential notice, or unsupported transaction claim.
Overall readiness is recorded in [`docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md); the final
evidence sequence is in the [`Shipaton runbook`](../docs/HACKATHON_RUNBOOK.md).

## Asset status

| Asset | Current status | Contract |
|---|---|---|
| `icon-1024.png` | Ready | Exactly 1024×1024, extracted byte-for-byte from the reviewed ICNS 1024 px chunk |
| `screenshot-1179x2556.png` | Ready current candidate | Exactly 1179×2556, regenerated from the current native UX, sanitized, and visually reviewed in light and dark appearance; repeat after later visual changes |
| `evidence/unlocked-test-store-2026-08-04.png` | Valid baseline evidence | Genuine 1020×754 packaged Debug app after Test Store unlock; no key or customer identifier; not final-current-revision proof |
| `evidence/voiceover-restore-2026-08-04.png` | Valid baseline evidence | VoiceOver enabled with native Restore focus; manual async success/cancel/failure announcements remain pending |
| Public video | Pending | Public YouTube/Vimeo, at or below 1:50 target and under the official two-minute limit, packaged macOS app |
| `devpost-draft.md` | Ready with explicit placeholders | Product story and judging proof are drafted; do not publish or remove placeholders before final evidence exists |

The source now includes Profile Builder, notice import preview, opt-in security-scoped bookmark
continuity, review/comparison search and buyer/deadline filters, stable comparison-cell drill-down,
and terminal RevenueCat accessibility announcements/focus recovery. The current portrait capture
shows that complete locked pre-transaction surface. The dated unlocked and VoiceOver evidence
captures still predate the newest UX and remain baseline evidence only.

A fresh 2026-08-05 Release package from the current source passed embedded-core determinism and
contract checks, signature verification, and worktree-independent smoke, and produced an `.app`,
zip, and checksum. The current portrait/icon asset gate also passes. A fresh final-revision Debug
Test Store and asynchronous accessibility pass remains separate manual evidence.

The final candidate must emit `NEXT_GEN_CHECKS_OK checks=15`; the suite now includes pure Premium
announcement, recovery-action, and focus-state outcomes in addition to the portfolio/input checks.

## Organizer proof

- [Shipaton Manager answer: Test Store-only purchase is acceptable](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient)
- [Shipaton answer: macOS is eligible with no platform-only disadvantage](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission)

Preserve the full dated threads. These answers resolve only the Test Store and platform
interpretations; they do not substitute for academic-email eligibility or final submission checks.

## Regenerate and validate

Build the final revision first, then regenerate the portrait candidate:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --render-submission-screenshot \
  "$PWD/submission/screenshot-1179x2556.png"
python3 tools/prepare_submission_assets.py
python3 tools/check_public_tree.py
```

The sanitizer removes ancillary PNG metadata chunks without changing `IHDR`, `IDAT`, or `IEND`
image data. The public-tree gate verifies exact dimensions and PNG structure; it cannot replace a
human visual check of clipping, hierarchy, focus, contrast, or truthful entitlement state.

For the final entry, use the exact current portrait screenshot and, if the form permits multiple
images, supplement it with a genuine unlocked Test Store capture from the final Debug package. Do
not use a hidden launch flag, edited entitlement, mock purchase, or composited fake as transaction
evidence.
