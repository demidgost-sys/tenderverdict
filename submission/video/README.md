# TenderVerdict Shipaton video package

This directory is the local, production-ready handoff for the English Shipaton demo. The current
local review master is a **1:49 video with the owner's human narration and burned English captions**.
It uses live Release-app footage for the product walkthrough and genuine sanitized evidence cards
for the RevenueCat section. The repaired v2 was published at the canonical YouTube URL and used in
the submitted Devpost entry; raw local MP4 and WAV files remain ignored.

The reproducible silent animatic remains the timing and evidence fallback. The final local review
master replaces the first 48 seconds with a current packaged-app window recording without changing
the approved claims or 109-second runtime.

## Start here

| Need | File |
|---|---|
| Exact 1:49 story and evidence | [Beat sheet](BEAT_SHEET.md) |
| Capture order and replacement notes | [Shot list](SHOT_LIST.md) |
| Approved on-screen wording | [Callouts](CALLOUTS.md) |
| Canonical English words | [Narration text](narration-en.txt) |
| Narration timing and delivery | [Narration guide](NARRATION_EN.md) |
| Owner recording instructions | [Human voice guide](HUMAN_VOICE_RECORDING_GUIDE_RU.md) |
| Readable eight-block script | [Human voice marked script](HUMAN_VOICE_MARKED_SCRIPT_EN.md) |
| Offline silent teleprompter | [Human voice teleprompter](human-voice-teleprompter.html) |
| Machine-readable recording cues | [Human voice cues](human-voice-cues.tsv) |
| Session notes and select log | [Human voice take log](HUMAN_VOICE_TAKE_LOG.md) |
| Russian editor handoff | [Director handoff](DIRECTOR_HANDOFF_RU.md) |
| English captions | [SRT captions](captions-en.srt) |
| Claim-to-source and file provenance | [Asset manifest](ASSET_MANIFEST.md) |
| Privacy review | [Privacy crop checklist](PRIVACY_CROP_CHECKLIST.md) |
| Full-resolution picture review | [Visual QA](VISUAL_QA.md) |
| Existing-material audit | [Audit](AUDIT.md) |
| Silent assembly contract | [Rough-cut plan](SILENT_ROUGH_CUT_PLAN.md) |
| Superseded AI fallback research | [AI voice options](AI_VOICE_OPTIONS.md) |

## Review outputs

- `tenderverdict-final-review-v2.mp4` — recommended local SSD-cache artifact outside the
  repository: 1920×1080, 30 fps, 1:49 H.264/AAC review master with the repaired human narration
  and burned English captions; not tracked, hosted with link access at
  `https://www.youtube.com/watch?v=HFBtMsN7Nlk`, and used in the submitted Devpost entry.
- `tenderverdict-final-review-v1.mp4` — superseded local review master with abrupt phrase-boundary
  edits; its upload is private and excluded from Devpost.
- `tenderverdict-silent-rough-cut-v1.mp4` — exact 1920×1080, 30 fps, 1:49 silent animatic;
  intentionally ignored and untracked because the public-tree policy rejects tracked files over
  1 MiB.
- `tenderverdict-silent-rough-cut-v1.local-receipt.txt` — ignored local receipt with the absolute
  path, SHA-256, size, runtime, audio-stream count, and ffprobe JSON.
- `silent-rough-cut-contact-sheet.png` — ten-frame visual QA sheet.
- `OUTPUT_QA.md` — committed public-safe runtime, ffprobe stream, caption, asset, and hash receipt.
- `human-voice-takes/` — ignored local destination for owner-recorded raw WAV files.
- `tenderverdict-vo-human-v2-natural.wav` — recommended ignored 109-second human voice master
  assembled only from the owner's supplied AIFC, with source-room-tone continuity and soft phrase
  boundaries, without time-stretch or generated speech.
- `tenderverdict-vo-human-v1.wav` — superseded voice master retained only for comparison.
- `FINAL_VIDEO_QA.md` — public-safe local-master metadata, provenance, caption, owner acceptance,
  and submitted-entry receipt.

## Rebuild and validate

These commands render images only and explicitly map no audio:

```bash
submission/video/build_silent_rough_cut.sh
python3 submission/video/validate_package.py
```

The validator fails if the MP4 contains an audio stream, reaches 1:50, disagrees with the SRT,
human cue sheet, or teleprompter, or uses an asset whose committed SHA-256 or dimensions differ
from `asset-manifest.json`.

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
- Use only the owner's recorded performance for narration. Do not generate or clone a voice.
- The hosted v2, owner watch/listen, truthful private-form resolution, final Submit, and logged-out
  Devpost URL readback are complete.
