# TenderVerdict Shipaton video package

This directory is the local, production-ready handoff for the English Shipaton demo. The current
review artifact is a **silent 1:49 animatic** assembled from genuine, sanitized application captures.
It contains no audio stream and is not uploaded or submitted.

The animatic proves the story and timing. It does not pretend that still images are continuous app
footage. The final editor may replace the marked shots with current packaged-app screen recordings
without changing the narration, captions, claims, or runtime.

## Start here

| Need | File |
|---|---|
| Exact 1:49 story and evidence | [Beat sheet](BEAT_SHEET.md) |
| Capture order and replacement notes | [Shot list](SHOT_LIST.md) |
| Approved on-screen wording | [Callouts](CALLOUTS.md) |
| Canonical English words | [Narration text](narration-en.txt) |
| Narration timing and delivery | [Narration guide](NARRATION_EN.md) |
| Russian editor handoff | [Director handoff](DIRECTOR_HANDOFF_RU.md) |
| English captions | [SRT captions](captions-en.srt) |
| Claim-to-source and file provenance | [Asset manifest](ASSET_MANIFEST.md) |
| Privacy review | [Privacy crop checklist](PRIVACY_CROP_CHECKLIST.md) |
| Full-resolution picture review | [Visual QA](VISUAL_QA.md) |
| Existing-material audit | [Audit](AUDIT.md) |
| Silent assembly contract | [Rough-cut plan](SILENT_ROUGH_CUT_PLAN.md) |
| Voice recommendation and license notes | [AI voice options](AI_VOICE_OPTIONS.md) |

## Review outputs

- `tenderverdict-silent-rough-cut-v1.mp4` — exact 1920×1080, 30 fps, 1:49 silent animatic;
  intentionally ignored and untracked because the public-tree policy rejects tracked files over
  1 MiB.
- `tenderverdict-silent-rough-cut-v1.local-receipt.txt` — ignored local receipt with the absolute
  path, SHA-256, size, runtime, audio-stream count, and ffprobe JSON.
- `silent-rough-cut-contact-sheet.png` — ten-frame visual QA sheet.
- `OUTPUT_QA.md` — committed public-safe runtime, ffprobe stream, caption, asset, and hash receipt.

## Rebuild and validate

These commands render images only and explicitly map no audio:

```bash
submission/video/build_silent_rough_cut.sh
python3 submission/video/validate_package.py
```

The validator fails if the MP4 contains an audio stream, reaches 1:50, disagrees with the SRT, or
uses an asset whose committed SHA-256 or dimensions differ from `asset-manifest.json`.

The MP4 is a local handoff artifact, not a public-tree asset. Do not add it to Git or to
`PUBLIC_TREE_ALLOWLIST.txt`.

## Non-negotiable boundaries

- Use only the committed synthetic fixtures and the sanitized evidence listed in the manifest.
- Keep **Test Store**, **Judge Access**, and **no real charge / no purchase** visually distinct.
- RevenueCat controls access to Portfolio presentation; it never changes a TenderVerdict result.
- Do not claim legal advice, award prediction, scoring, ranking, automatic bidding, production
  billing, notarization, public release, or spoken VoiceOver verification.
- Do not show or store a RevenueCat key, reviewer code, account email, customer identifier,
  dashboard, terminal, notification, or private notice.
- Do not generate, play, record, or add speech until the owner explicitly chooses and authorizes a
  voice route.
- Publication, upload, Devpost editing, and RevenueCat/account actions remain separate owner gates.
