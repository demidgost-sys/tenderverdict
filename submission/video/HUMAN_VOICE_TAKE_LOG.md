# Human voice take log

- Session date: `2026-08-09`
- Continuous session filename (if used): `Tenderverdikt.aifc` (private source held outside the repository)
- Microphone/interface: `________________`
- Room/location: `________________`
- Recorder settings observed: `48 kHz / PCM 16-bit / mono`
- Room tone source: opening silence from the unchanged AIFC
- Raw source SHA-256: `345926cbf5f2f52125b0a79616f3495c29ab8756141cf28f9dd0f1108af62b7a`

The owner may leave this log blank. During assembly, use `OK`, `pickup`, or a short fault note. Do
not delete raw takes during or after the session.

| Block | T01 | T02 | Pickup filename | Selected take | Notes |
|---:|---|---|---|---|---|
| 01 Problem | source 09.94–18.00 |  |  | T01 | Clean full block |
| 02 Local workflow | source 24.08–35.06 |  |  | T01 | Clean full block |
| 03 Three verdicts | source 38.86–51.12 |  |  | T01 | Clean full block |
| 04 Free | source 56.24–66.74 |  |  | T01 | Clean full block |
| 05 Portfolio | failed start 71.80–75.40 | source 83.68–99.06 |  | T02 | Removed the conflicting words “changed a verdict” from the owner take; no generated speech |
| 06 Test Store | source 101.98–117.92 |  |  | T01 | Clean full block |
| 07 Judge Access | source 121.06–130.26 |  | source 140.62–147.22 | T01 + pickup | Later Restore/relaunch pickup replaces the earlier tail |
| 08 Safety/license | source 150.45–163.39 |  |  | T01 | Three continuous source phrases; no word-level reconstruction |

## Assembly receipt

- [x] Selected words match `narration-en.txt` exactly after the documented owner-voice edits.
- [x] Master begins at timeline zero and ends at `00:01:49.000`.
- [x] One mono PCM 24-bit / 48 kHz audio stream; no video stream.
- [x] No time-stretch, synthetic replacement, music, or SFX.
- [x] Metadata-only validator passed.
- [ ] Owner completed a normal-speed listening pass.

Selected v2 master SHA-256: `4a3d32f8aa40809f9c34423ed35728d1625f3830b95c3676a3a3bee63c8b9e2f`

The v2 assembly preserves pre-roll and post-roll around phrases, carries continuous source room
tone across the timeline, and uses soft boundary fades. Block 08 uses three continuous recorded
phrases instead of the superseded v1 word-level reconstruction.
