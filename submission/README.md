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
| `evidence/voiceover-restore-2026-08-04.png` | Valid baseline evidence | VoiceOver enabled with native Restore focus; manual async success/cancel/failure announcements are unverified optional follow-up evidence |
| `evidence/unlocked-judge-access-2026-08-09.png` | Ready current evidence | Genuine 1020×754 exact `cbe8b20` Judge Access screen after refresh, Restore, foreground, and relaunch; no purchase, key, reviewer code, or customer identifier |
| `video/` | Ready local production handoff | Exact 1:49 silent animatic, owner-recording kit, narration, captions, manifests, privacy/claim audit, contact sheet, and QA receipt; raw MP4/WAV stay ignored and are not public video assets |
| `linkedin-project-story.md` | Published by owner; readback not independently audited | Human first-person Shipaton project story with no recruitment or user-validation claim |
| Public video | Pending | Public YouTube/Vimeo, at or below 1:50 target and under the official two-minute limit, packaged macOS app |
| `devpost-draft.md` | Ready with explicit placeholders | Product story and judging proof are drafted; do not publish or remove placeholders before final evidence exists |

The source now includes Profile Builder, notice import preview, opt-in security-scoped bookmark
continuity, review/comparison search and buyer/deadline filters, stable comparison-cell drill-down,
and terminal RevenueCat accessibility announcements/focus recovery. The portrait capture shows the
complete Free and locked Portfolio surface; the current Judge Access capture leads the
cross-profile story with a genuine unlocked comparison. The dated Test Store and VoiceOver
captures remain baseline evidence.

The clean release-configuration package named in project status passed
configuration-specific native checks, embedded-core determinism and contracts, signature,
checksum, ZIP integrity, and worktree-independent smoke. Its `.app`, zip, exact SHA-256, and
manifest live in [`docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md). The portrait/icon asset gate
also passes. Clean `3cf20ed` remains the purchase/cancel/failure baseline, while clean `cbe8b20`
covers the current granted-entitlement refresh, Restore, foreground, relaunch, and silent
accessibility-tree evidence. Hands-on VoiceOver announcements remain an optional accessibility
follow-up rather than a submission gate.

The video handoff in [`video/`](video/) is locally complete and remains fully silent. The owner has
selected a self-recorded human voice; the marked script, teleprompter, take log, recording format,
and metadata-only stem validator are prepared. The public-video gate remains pending until that
voice is recorded, the complete file is reviewed at normal speed with sound, and an owner-authorized
YouTube/Vimeo upload passes logged-out verification.

The authenticated Devpost field inventory and saved-draft readback are complete. Current readiness
and the required store-release attestation conflict are tracked only in
[`docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md); no private account value is copied here.

The final candidate must emit `NEXT_GEN_CHECKS_OK` in Debug and Release; the current expected total
is recorded only in project status. The suite includes display safety, schema-3 Free export
isolation, exact RevenueCat identifiers, and pure Portfolio announcement/recovery/focus outcomes.

## Organizer proof

- [Shipaton Manager answer: Test Store-only purchase is acceptable](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient)
- [Shipaton answer: macOS is eligible with no platform-only disadvantage](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission)

Preserve the full dated threads. These answers resolve only the Test Store and platform
interpretations; they do not resolve the separate required store-release attestation, public-video,
or final-submission gates.

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

For the final entry, keep the exact 1179×2556 portrait for any required portrait slot. Where the
gallery permits a landscape lead or multiple images, lead with
`evidence/unlocked-judge-access-2026-08-09.png` so the cross-profile value is visible immediately,
then use the portrait for the complete Free-to-Portfolio workflow. Label Judge Access as a granted
entitlement, not a purchase. Do not use a hidden launch flag, edited entitlement, mock purchase, or
composited fake as transaction evidence.
