# Silent source audit — 2026-08-09

## Outcome

The available still captures are sufficient for a truthful 1:49 silent animatic and a complete
edit decision list. They are not sufficient to represent a continuous final app demonstration.
The final editor should replace five marked still shots with current packaged-app recordings while
preserving the approved text and timing.

No audio was played. The audit used file listings, hashes, image inspection, and `ffprobe` metadata
only.

## Existing draft

Source directory supplied for the audit: `TenderVerdict Demo Draft/` (kept outside the public
repository).

| Item | Observed result | Use in this package |
|---|---|---|
| `TenderVerdict-Shipaton-demo-draft.mp4` | 1920×1080 H.264, 30 fps, 62.400 s; includes one AAC audio stream | Do not reuse as the silent master |
| `narration.aiff` | 61.518 s mono PCM, detected by metadata only | Excluded; never played or copied |
| `captions.srt` | Seven cues ending at 1:06 | Superseded by the 1:49 evidence-backed script |
| Seven rendered slides | Genuine baseline app captures inside designed cards | Reference only; several claims/revisions are stale |
| `review-contact-sheet.png` | Confirms readable overall style, but UI details are small and one transition sample overlaps text | Reference only |

## Why the old cut is not final

1. Its README says 66 seconds while the actual file is 62.400 seconds.
2. It contains audio, so it violates this pass's silent-only contract.
3. Its source revision is `13e5ec2`; the current product evidence is `cbe8b20`, and the package
   branch starts at `217c091`.
4. The baseline unlocked frame shows a `1 Open / 0 Watch / 2 Reject` profile, while the current
   canonical submission render shows `1 / 1 / 1`. Both may be historical truths, but mixing them
   without dates looks contradictory.
5. “VoiceOver exposed…” is not allowed as a current spoken-accessibility claim: the 2026-08-09
   audit intentionally remained silent and says the post-change spoken outcomes are unverified.
6. It does not clearly show the problem, normalized local source, actual comparison matrix, current
   Judge Access copy, or the separation between an older Test Store purchase baseline and the
   current no-purchase entitlement grant.
7. “Clean release gates passed” is too broad without the exact evaluation-build boundary and can be
   mistaken for notarized public-release readiness.

## Reviewed visual sources

| Source | Evidence class | Findings |
|---|---|---|
| `submission/screenshot-1179x2556.png` | Current deterministic submission render | Best source for problem, local workflow, Free value, and the three verdicts; synthetic and sanitized |
| `demo/screenshot.png` | Current static report render | Useful supplemental provenance/three-verdict image; not native app footage |
| `submission/evidence/unlocked-judge-access-2026-08-09.png` | Current genuine `cbe8b20` manual capture | Best source for comparison, RevenueCat Judge Access, Restore, and literal “No purchase was made” copy |
| `submission/evidence/unlocked-test-store-2026-08-04.png` | Dated genuine baseline | Valid for a historical Test Store entitlement outcome only; not current-revision purchase proof |
| `assets/test-store-purchase-sheet-baseline-2026-08-04.jpg` | Dated genuine baseline, losslessly metadata-stripped | Decoded-pixel SHA-256 matches the original; the sheet says development/test and shows only public-safe product/price details |
| `assets/entitlement-restored-on-relaunch-baseline-2026-08-04.jpg` | Dated genuine baseline, losslessly metadata-stripped | Decoded-pixel SHA-256 matches the original; supports the historical relaunch state while the current result remains audit-owned |

## Missing continuous footage

The package does not currently contain a screen recording of Profile Builder, import preview,
filter interaction, Test Store transition, comparison-cell drill-down, or relaunch. The animatic
labels every still honestly. The replacement capture plan is in `SHOT_LIST.md`; no account action
or new transaction is required to approve the script or narration.
