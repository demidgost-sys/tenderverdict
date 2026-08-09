# Final local video QA receipt

- Status: **local review master created; not uploaded, published, or submitted**
- Recommended upload filename: `tenderverdict-final-review-v1.mp4`
- Local runtime: `109.000 s` / `00:01:49.000`
- Encoded size: `5,007,333 bytes`
- Video: `H.264 High`, `1920x1080`, `30 fps`, `yuv420p`
- Audio: `AAC-LC`, `48 kHz`, `mono`, approximately `165 kb/s`
- Integrated loudness: `-16.4 LUFS`; loudness range `3.8 LU`; true peak `-1.3 dBFS`
- Final MP4 SHA-256: `e1922cf6d910c5ef5589b72cdafe87f5d80422afad0f1d1d81e5e8cf767e60ab`
- Human voice stem SHA-256: `7edfd139ab0998ca06ccca091f1aabc6152a6eb46e8b281bfc48a1b88e2d420f`
- Unchanged owner AIFC SHA-256: `345926cbf5f2f52125b0a79616f3495c29ab8756141cf28f9dd0f1108af62b7a`

## Picture and privacy

- `00:00–00:48`: app-window-only Release capture built from commit
  `dbeed5de23fbc0547199e0ec2111a75fe2f7c87b`; synthetic guided example only.
- `00:48–01:49`: sanitized, manifest-checked RevenueCat evidence cards and deterministic end card.
- A 12-frame contact sheet was inspected at full resolution. No desktop, terminal, notification,
  account email, RevenueCat key, reviewer code, customer identifier, or private tender is visible.

## Voice and captions

- The source AIFC remains unchanged. Failed starts and the earlier incorrect tails were excluded;
  the later owner retakes were selected.
- The voice stem contains only the owner's recorded voice plus the recording's own room tone. No
  voice synthesis, cloning, time-stretch, music, or sound effects were used.
- Eighteen English caption cues are burned into the MP4. Their normalized text exactly matches
  `captions-en.srt`, `narration-en.txt`, the eight-block cue sheet, marked script, and teleprompter.
- The canonical narration is `196 words` at `107.9 timeline words/min`.

## Remaining owner gate

- [ ] Watch and listen once at normal speed before any upload.
- [ ] If accepted, upload the MP4 above; keep `captions-en.srt` as the matching sidecar transcript.
- [ ] Publishing, Devpost editing/submission, and repository changes remain outside this video pass.
