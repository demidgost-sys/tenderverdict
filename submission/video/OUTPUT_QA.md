# Silent rough-cut QA receipt

- Checked at: `2026-08-09T16:26:51+00:00`
- Timeline: `109.000 s` / `00:01:49.000`
- Local artifact: `tenderverdict-silent-rough-cut-v1.mp4` (repository-relative; ignored/untracked)
- Git/public-tree state: **ignored and untracked; never add to the allowlist**
- Encoded MP4: `109.000 s`, `1920x1080`, `30 fps`, `H.264`
- Encoded size: `4260971 bytes`
- Audio streams: **0**
- Narration/captions: `201 words`, `17 cues`, exact text match
- Timeline delivery density: `110.6 words/min`
- Human voice plan: `8 blocks`, exact SRT/marked-script/TSV/HTML match, maximum target pace `151.6 words/min`
- Source assets: `7` hash/dimension checks passed
- Video SHA-256: `9be79aa90f071bd878aeb74e672c25e3fdbfa5537e18a509a8601caee2c43e4a`
- Contact sheet: `1920x432`, SHA-256 `9169921139c04a54d340838a217e4d40f4945baaaf351630a7dda4e4c7e753c4`
- Publication/upload/account actions: **not performed**

The MP4 is a silent evidence animatic built from still captures. It is not continuous final app footage.

## ffprobe receipt

Command:

```bash
ffprobe -v error -show_entries format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate -of json tenderverdict-silent-rough-cut-v1.mp4
```

```json
{
  "format": {
    "duration": "109.000000",
    "size": "4260971"
  },
  "programs": [],
  "stream_groups": [],
  "streams": [
    {
      "avg_frame_rate": "30/1",
      "codec_name": "h264",
      "codec_type": "video",
      "height": 1080,
      "index": 0,
      "width": 1920
    }
  ]
}
```
