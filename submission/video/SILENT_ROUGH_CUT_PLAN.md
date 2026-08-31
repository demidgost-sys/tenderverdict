# Silent rough-cut assembly contract

## Deliverable

- 1920×1080, 30 fps, H.264, yuv420p.
- Exact duration: **109.000 seconds**.
- One video stream; **zero audio streams**.
- No embedded subtitle stream; `captions-en.srt` is the reviewable sidecar.
- Ten deterministic cards built from original evidence plus separate exact callout layers.
- Hard cuts preserve the time map. A final editor may use sub-200 ms dissolves only if the total
  runtime remains 109.000 seconds.

## Track map

| Track | Current state | Final use |
|---|---|---|
| V1 | Deterministic evidence cards | Replace marked shots with packaged-app footage |
| V2 | Callouts rendered into each card | Keep exact wording and qualifier labels |
| C1 | `captions-en.srt` sidecar | Import as captions; do not auto-rewrite |
| A1 | **Absent** | Add the owner's dry human voice stem after recording and QA |
| A2 | **Absent** | No music or SFX planned |

## Reproducibility

`render_cards.swift` reads `timeline.json` and draws only raster/video-frame output. The build script
passes `-an`, maps only `[vout]`, and validates the result. `asset-manifest.json` pins every source
PNG by size and SHA-256. `validate_package.py` checks:

1. asset hashes and dimensions;
2. timeline total and official runtime limits;
3. continuous SRT timing and text identity with `narration-en.txt`;
4. eight-block human cue continuity, recording pace, and teleprompter text identity;
5. MP4 resolution, frame rate, duration, and absence of audio;
6. contact-sheet dimensions and output hashes.

The animatic does not reuse the prior narrated MP4 or its AIFF file.
