#!/usr/bin/env python3
"""Validate final human voice-stem metadata without playing or transcribing audio."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


EXPECTED_DURATION = 109.0
EXPECTED_CODEC = "pcm_s24le"
EXPECTED_SAMPLE_RATE = "48000"
EXPECTED_CHANNELS = 1


def fail(message: str) -> None:
    raise SystemExit(f"HUMAN_VOICE_STEM_FAIL {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, object]:
    try:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                (
                    "format=duration,size,format_name:"
                    "stream=index,codec_type,codec_name,sample_rate,channels,bits_per_raw_sample"
                ),
                "-of",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail("ffprobe_not_found")
    except subprocess.CalledProcessError as error:
        fail(f"ffprobe_error detail={error.stderr.strip()}")
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("voice_stem", type=Path)
    arguments = parser.parse_args()
    voice_stem = arguments.voice_stem.resolve()

    if not voice_stem.is_file():
        fail(f"missing_file path={voice_stem}")
    if voice_stem.suffix.casefold() != ".wav":
        fail(f"container expected=wav actual={voice_stem.suffix or '[none]'}")

    receipt = probe(voice_stem)
    streams = receipt.get("streams", [])
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    other_streams = [stream for stream in streams if stream.get("codec_type") != "audio"]
    if len(audio_streams) != 1 or other_streams:
        fail(f"stream_layout audio={len(audio_streams)} other={len(other_streams)}")

    stream = audio_streams[0]
    if stream.get("codec_name") != EXPECTED_CODEC:
        fail(f"codec expected={EXPECTED_CODEC} actual={stream.get('codec_name')}")
    if stream.get("sample_rate") != EXPECTED_SAMPLE_RATE:
        fail(
            f"sample_rate expected={EXPECTED_SAMPLE_RATE} actual={stream.get('sample_rate')}"
        )
    if stream.get("channels") != EXPECTED_CHANNELS:
        fail(f"channels expected={EXPECTED_CHANNELS} actual={stream.get('channels')}")
    if stream.get("bits_per_raw_sample") not in {"24", None}:
        fail(f"bit_depth expected=24 actual={stream.get('bits_per_raw_sample')}")

    format_data = receipt.get("format", {})
    duration = float(format_data.get("duration", 0.0))
    if abs(duration - EXPECTED_DURATION) > 0.05:
        fail(f"duration expected={EXPECTED_DURATION:.3f} actual={duration:.3f}")
    if "wav" not in str(format_data.get("format_name", "")).split(","):
        fail(f"format expected=wav actual={format_data.get('format_name')}")

    print(
        "HUMAN_VOICE_STEM_OK "
        f"duration={duration:.3f} codec={stream.get('codec_name')} "
        f"sample_rate={stream.get('sample_rate')} channels={stream.get('channels')} "
        f"size={voice_stem.stat().st_size} sha256={sha256(voice_stem)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
