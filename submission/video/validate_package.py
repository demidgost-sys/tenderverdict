#!/usr/bin/env python3
"""Validate the deterministic, silent TenderVerdict Shipaton video handoff."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
TIMELINE_PATH = PACKAGE_ROOT / "timeline.json"
MANIFEST_PATH = PACKAGE_ROOT / "asset-manifest.json"
NARRATION_PATH = PACKAGE_ROOT / "narration-en.txt"
CAPTIONS_PATH = PACKAGE_ROOT / "captions-en.srt"
VIDEO_PATH = PACKAGE_ROOT / "tenderverdict-silent-rough-cut-v1.mp4"
CONTACT_SHEET_PATH = PACKAGE_ROOT / "silent-rough-cut-contact-sheet.png"
REPORT_PATH = PACKAGE_ROOT / "OUTPUT_QA.md"
LOCAL_REPORT_PATH = PACKAGE_ROOT / "tenderverdict-silent-rough-cut-v1.local-receipt.txt"
EXPECTED_RUNTIME = 109.0


def fail(message: str) -> None:
    raise SystemExit(f"VIDEO_PACKAGE_FAIL {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raster_format_and_dimensions(path: Path) -> tuple[str, int, int]:
    data = path.read_bytes()
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return "png", width, height
    if len(data) >= 4 and data[:2] == b"\xff\xd8":
        offset = 2
        sof_markers = {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            while marker == 0xFF and offset < len(data):
                marker = data[offset]
                offset += 1
            if marker in {0xD8, 0xD9}:
                continue
            if offset + 2 > len(data):
                break
            segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
            if marker in sof_markers and offset + 7 <= len(data):
                height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
                return "jpeg", width, height
            if segment_length < 2:
                break
            offset += segment_length
    fail(f"unsupported_raster path={path}")


def timestamp_to_seconds(value: str) -> float:
    match = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", value)
    if not match:
        fail(f"invalid_srt_timestamp value={value}")
    hours, minutes, seconds, milliseconds = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    cues: list[tuple[float, float, str]] = []
    for expected_index, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(expected_index):
            fail(f"invalid_srt_block index={expected_index}")
        timing = re.fullmatch(
            r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",
            lines[1],
        )
        if not timing:
            fail(f"invalid_srt_timing index={expected_index}")
        start = timestamp_to_seconds(timing.group(1))
        end = timestamp_to_seconds(timing.group(2))
        if end <= start:
            fail(f"nonpositive_srt_cue index={expected_index}")
        text = " ".join(line.strip() for line in lines[2:] if line.strip())
        cues.append((start, end, text))
    return cues


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def ffprobe(path: Path) -> dict[str, object]:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


timeline = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
shots = timeline.get("shots", [])
if len(shots) != 10:
    fail(f"shot_count actual={len(shots)} expected=10")
runtime = sum(float(shot["duration"]) for shot in shots)
if abs(runtime - EXPECTED_RUNTIME) > 0.0001:
    fail(f"timeline_runtime actual={runtime:.3f} expected={EXPECTED_RUNTIME:.3f}")
if runtime >= 110 or runtime >= 120:
    fail(f"runtime_limit actual={runtime:.3f}")

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
manifest_paths: set[str] = set()
asset_receipts: list[tuple[str, str, int, int]] = []
for asset in manifest.get("assets", []):
    relative_path = str(asset["path"])
    manifest_paths.add(relative_path)
    asset_path = (PACKAGE_ROOT / relative_path).resolve()
    if not asset_path.is_file():
        fail(f"missing_asset path={relative_path}")
    actual_hash = sha256(asset_path)
    if actual_hash != asset["sha256"]:
        fail(f"asset_hash path={relative_path} actual={actual_hash}")
    actual_format, width, height = raster_format_and_dimensions(asset_path)
    if actual_format != asset["format"]:
        fail(
            f"asset_format path={relative_path} actual={actual_format} "
            f"expected={asset['format']}"
        )
    if width != asset["width"] or height != asset["height"]:
        fail(
            f"asset_dimensions path={relative_path} actual={width}x{height} "
            f"expected={asset['width']}x{asset['height']}"
        )
    asset_receipts.append((relative_path, actual_hash, width, height))

for shot in shots:
    if shot["source"] not in manifest_paths:
        fail(f"unmanifested_timeline_source shot={shot['id']} path={shot['source']}")

cues = parse_srt(CAPTIONS_PATH)
if abs(cues[0][0]) > 0.0001:
    fail(f"captions_start actual={cues[0][0]:.3f}")
for index in range(1, len(cues)):
    if abs(cues[index][0] - cues[index - 1][1]) > 0.0001:
        fail(f"captions_gap before={index + 1}")
if abs(cues[-1][1] - EXPECTED_RUNTIME) > 0.0001:
    fail(f"captions_end actual={cues[-1][1]:.3f}")

narration = normalize_text(NARRATION_PATH.read_text(encoding="utf-8"))
caption_text = normalize_text(" ".join(cue[2] for cue in cues))
if narration != caption_text:
    fail("caption_text_does_not_match_narration")
word_count = len(re.findall(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*", narration))
timeline_wpm = word_count / (EXPECTED_RUNTIME / 60)

if not VIDEO_PATH.is_file():
    fail(f"missing_video path={VIDEO_PATH.name}")
probe = ffprobe(VIDEO_PATH)
streams = probe.get("streams", [])
video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
if len(video_streams) != 1:
    fail(f"video_stream_count actual={len(video_streams)}")
if audio_streams:
    fail(f"audio_stream_count actual={len(audio_streams)}")
video_stream = video_streams[0]
if video_stream.get("width") != 1920 or video_stream.get("height") != 1080:
    fail(
        f"video_dimensions actual={video_stream.get('width')}x{video_stream.get('height')}"
    )
if video_stream.get("avg_frame_rate") != "30/1":
    fail(f"video_fps actual={video_stream.get('avg_frame_rate')}")
video_duration = float(probe["format"]["duration"])
if abs(video_duration - EXPECTED_RUNTIME) > 0.05:
    fail(f"video_runtime actual={video_duration:.3f}")

if not CONTACT_SHEET_PATH.is_file():
    fail(f"missing_contact_sheet path={CONTACT_SHEET_PATH.name}")
contact_format, contact_width, contact_height = raster_format_and_dimensions(CONTACT_SHEET_PATH)
if contact_format != "png":
    fail(f"contact_sheet_format actual={contact_format}")
if (contact_width, contact_height) != (1920, 432):
    fail(f"contact_sheet_dimensions actual={contact_width}x{contact_height}")

video_hash = sha256(VIDEO_PATH)
contact_hash = sha256(CONTACT_SHEET_PATH)
video_size = VIDEO_PATH.stat().st_size
checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
ffprobe_receipt = json.dumps(probe, indent=2, sort_keys=True)
report_lines = [
    "# Silent rough-cut QA receipt",
    "",
    f"- Checked at: `{checked_at}`",
    f"- Timeline: `{runtime:.3f} s` / `00:01:49.000`",
    f"- Local artifact: `{VIDEO_PATH.name}` (repository-relative; ignored/untracked)",
    "- Git/public-tree state: **ignored and untracked; never add to the allowlist**",
    f"- Encoded MP4: `{video_duration:.3f} s`, `1920x1080`, `30 fps`, `H.264`",
    f"- Encoded size: `{video_size} bytes`",
    "- Audio streams: **0**",
    f"- Narration/captions: `{word_count} words`, `{len(cues)} cues`, exact text match",
    f"- Timeline delivery density: `{timeline_wpm:.1f} words/min`",
    f"- Source assets: `{len(asset_receipts)}` hash/dimension checks passed",
    f"- Video SHA-256: `{video_hash}`",
    f"- Contact sheet: `1920x432`, SHA-256 `{contact_hash}`",
    "- Publication/upload/account actions: **not performed**",
    "",
    "The MP4 is a silent evidence animatic built from still captures. It is not continuous final app footage.",
    "",
    "## ffprobe receipt",
    "",
    "Command:",
    "",
    "```bash",
    "ffprobe -v error -show_entries format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate -of json tenderverdict-silent-rough-cut-v1.mp4",
    "```",
    "",
    "```json",
    ffprobe_receipt,
    "```",
    "",
]
REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

local_report_lines = [
    "TenderVerdict silent rough-cut local receipt",
    f"checked_at={checked_at}",
    f"absolute_path={VIDEO_PATH}",
    f"size_bytes={video_size}",
    f"sha256={video_hash}",
    f"duration_seconds={video_duration:.6f}",
    "audio_streams=0",
    "git_state=ignored_and_untracked",
    "ffprobe_json=",
    ffprobe_receipt,
    "",
]
LOCAL_REPORT_PATH.write_text("\n".join(local_report_lines), encoding="utf-8")

print(
    "VIDEO_PACKAGE_OK "
    f"runtime={video_duration:.3f} words={word_count} wpm={timeline_wpm:.1f} "
    f"audio_streams=0 assets={len(asset_receipts)} sha256={video_hash}"
)
