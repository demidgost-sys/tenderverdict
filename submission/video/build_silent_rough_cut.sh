#!/bin/zsh
set -euo pipefail

package_root="${0:A:h}"
output_path="$package_root/tenderverdict-silent-rough-cut-v1.mp4"
contact_sheet_path="$package_root/silent-rough-cut-contact-sheet.png"
temp_dir="$(mktemp -d /tmp/tenderverdict-video.XXXXXX)"
trap 'rm -rf "$temp_dir"' EXIT

for command_name in swift ffmpeg ffprobe python3; do
  command -v "$command_name" >/dev/null || {
    printf 'MISSING_TOOL %s\n' "$command_name" >&2
    exit 2
  }
done

swift "$package_root/render_cards.swift" \
  "$package_root/timeline.json" \
  "$temp_dir/cards" \
  "$temp_dir/shots.tsv"

typeset -a input_args
typeset filter_chain=""
typeset concat_inputs=""
integer input_index=0

while IFS=$'\t' read -r shot_id duration card_path; do
  [[ -n "$shot_id" && -n "$duration" && -f "$card_path" ]] || {
    printf 'INVALID_RENDER_ROW %s\n' "$shot_id" >&2
    exit 2
  }
  input_args+=(-loop 1 -framerate 30 -t "$duration" -i "$card_path")
  filter_chain+="[$input_index:v]scale=1920:1080:flags=lanczos,fps=30,format=yuv420p[v$input_index];"
  concat_inputs+="[v$input_index]"
  (( input_index += 1 ))
done < "$temp_dir/shots.tsv"

runtime="$(awk -F $'\t' '{total += $(2)} END {printf "%.3f", total}' "$temp_dir/shots.tsv")"
filter_chain+="${concat_inputs}concat=n=${input_index}:v=1:a=0[vout]"

ffmpeg -hide_banner -loglevel error -y \
  "${input_args[@]}" \
  -filter_complex "$filter_chain" \
  -map '[vout]' \
  -an \
  -t "$runtime" \
  -c:v libx264 \
  -preset medium \
  -crf 20 \
  -tune stillimage \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$output_path"

ffmpeg -hide_banner -loglevel error -y \
  -framerate 1 \
  -pattern_type glob \
  -i "$temp_dir/cards/*.png" \
  -vf 'scale=384:216:force_original_aspect_ratio=decrease,pad=384:216:(ow-iw)/2:(oh-ih)/2,tile=5x2' \
  -frames:v 1 \
  -update 1 \
  -an \
  "$contact_sheet_path"

python3 "$package_root/sanitize_png.py" "$contact_sheet_path"

python3 "$package_root/validate_package.py"

printf 'SILENT_ROUGH_CUT_OK path=%s runtime=%s audio_streams=0\n' "$output_path" "$runtime"
