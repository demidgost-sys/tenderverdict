# Silent rough-cut QA receipt

- Checked at: `2026-08-09T13:31:43+00:00`
- Timeline: `109.000 s` / `00:01:49.000`
- Local artifact: `tenderverdict-silent-rough-cut-v1.mp4` (repository-relative; ignored/untracked)
- Git/public-tree state: **ignored and untracked; never add to the allowlist**
- Encoded MP4: `109.000 s`, `1920x1080`, `30 fps`, `H.264`
- Encoded size: `4190035 bytes`
- Audio streams: **0**
- Narration/captions: `233 words`, `17 cues`, exact text match
- Timeline delivery density: `128.3 words/min`
- Human voice plan: `8 blocks`, exact SRT/marked-script/TSV/HTML match, maximum target pace `150.0 words/min`
- Source assets: `7` hash/dimension checks passed
- Video SHA-256: `1d3117032827ca06b37a930683d581d983bc467087e28b36fecb0dca28a5c15b`
- Contact sheet: `1920x432`, SHA-256 `a7014cbb73937bc79ca0294b12da002cd4701aa02bdd450f018e35bb44d749e3`
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
    "size": "4190035"
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
