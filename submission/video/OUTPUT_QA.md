# Silent rough-cut QA receipt

- Checked at: `2026-08-09T17:21:46+00:00`
- Timeline: `109.000 s` / `00:01:49.000`
- Local artifact: `tenderverdict-silent-rough-cut-v1.mp4` (repository-relative; ignored/untracked)
- Git/public-tree state: **ignored and untracked; never add to the allowlist**
- Encoded MP4: `109.000 s`, `1920x1080`, `30 fps`, `H.264`
- Encoded size: `4361711 bytes`
- Audio streams: **0**
- Narration/captions: `196 words`, `18 cues`, exact text match
- Timeline delivery density: `107.9 words/min`
- Human voice plan: `8 blocks`, exact SRT/marked-script/TSV/HTML match, maximum target pace `148.1 words/min`
- Source assets: `7` hash/dimension checks passed
- Video SHA-256: `16cde06633111081a06f9ac3f113d83b58dbd6a339164d62bb3de42c759310c5`
- Contact sheet: `1920x432`, SHA-256 `1fd4d3997644608225335a862ac35a9afaa7b08c6ae0c8c671e8e8be3c46abe7`
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
    "size": "4361711"
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
