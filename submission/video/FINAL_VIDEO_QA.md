# Final local video QA receipt

- Status: **v2 owner-approved, hosted with link access, and used in the submitted Devpost entry**
- Hosted video: `https://www.youtube.com/watch?v=HFBtMsN7Nlk`
- Recommended upload filename: `tenderverdict-final-review-v2.mp4`
- Local runtime: `109.000 s` / `00:01:49.000`
- Encoded size: `5,153,966 bytes`
- Video: `H.264 High`, `1920x1080`, `30 fps`, `yuv420p`
- Audio: `AAC-LC`, `48 kHz`, `mono`, approximately `176 kb/s`
- Integrated loudness: `-16.7 LUFS`; loudness range `3.5 LU`; true peak `-1.4 dBFS`
- Final MP4 SHA-256: `5862094c00c8dcb5e2e793d46d1ced44a003458dfcb1d957484135da13c6d047`
- Human voice stem SHA-256: `4a3d32f8aa40809f9c34423ed35728d1625f3830b95c3676a3a3bee63c8b9e2f`
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
- This v2 rebuild restores recorded handles around phrases, keeps room tone continuous, and adds
  soft boundary fades. Its final block uses three continuous owner-recorded phrases rather than the
  superseded v1 word-level reconstruction.
- Eighteen English caption cues are burned into the MP4. Their normalized text exactly matches
  `captions-en.srt`, `narration-en.txt`, the eight-block cue sheet, marked script, and teleprompter.
- The canonical narration is `196 words` at `107.9 timeline words/min`.

## Hosted handoff

- YouTube's upload check reports no violations; the matching English SRT is published alongside
  the burned captions.
- An unauthenticated oEmbed readback returns the expected v2 title with HTTP 200.
- Authenticated YouTube Studio readback reports the v2 source filename, `109` seconds, Unlisted
  visibility, and published English subtitles.
- The superseded v1 upload is private, excluded from Devpost, and returns HTTP 403 to the same
  unauthenticated oEmbed check. It remains retained only as a reversible audit artifact.
- Authenticated Devpost Project details readback contains the v2 URL. After the organizer corrected
  the contradictory required-field validation, store release remained false, final Submit
  succeeded, and authenticated plus logged-out project readbacks passed.

## Final submission handoff

- [x] Watch and listen to v2 once at normal speed before final submission use.
- [x] Keep the accepted hosted v2 and its matching `captions-en.srt`; do not restore v1 access.
- [x] Keep v2 in the submitted entry; the truthful private form and final Submit are verified in
  [`../DEVPOST_FINALIZATION_QA.md`](../DEVPOST_FINALIZATION_QA.md).
