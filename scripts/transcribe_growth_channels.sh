#!/usr/bin/env bash
# Transcribes videos from mobile growth / app founder YouTube channels.
# Run: bash scripts/transcribe_growth_channels.sh
# Adjust --since and --model to your needs.

set -euo pipefail

MODEL="${MODEL:-base}"        # override: MODEL=small bash ...
SINCE="${SINCE:-2024-04-30}"  # override: SINCE=2023-01-01 bash ...
OUTPUT_DIR="${OUTPUT_DIR:-./channel_transcriptions}"
USE_MLX="${USE_MLX:-}"        # set USE_MLX=1 to enable Apple Silicon acceleration

mkdir -p "$OUTPUT_DIR"

# Returns 0 (true) if the CSV already contains videos going back to $since_date,
# meaning no new fetching is needed for this channel.
channel_covered() {
  local csv="$1"
  local since="$2"  # YYYY-MM-DD
  [[ -f "$csv" ]] || return 1
  python3 - "$csv" "$since" <<'EOF'
import sys, csv
csv_file, since = sys.argv[1], sys.argv[2].replace('-', '')
dates = [
    row['Publish Date'].strip()
    for row in csv.DictReader(open(csv_file, newline='', encoding='utf-8'))
    if len(row.get('Publish Date', '').strip()) == 8 and row['Publish Date'].strip().isdigit()
]
sys.exit(0 if dates and min(dates) <= since else 1)
EOF
}

run_channel() {
  local name="$1"
  local url="$2"
  local slug
  slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
  local output="$OUTPUT_DIR/${slug}.csv"

  echo ""
  if channel_covered "$output" "$SINCE"; then
    echo ">>> [$name] already fully covered — skipping"
    return
  fi

  echo ">>> [$name] $url"
  echo "    Output: $output"

  local mlx_flag=""
  [[ -n "$USE_MLX" ]] && mlx_flag="--use-mlx"

  vidscribe playlist "$url" \
    --output "$output" \
    --model "$MODEL" \
    --since "$SINCE" \
    $mlx_flag

  echo "    Done: $output"
}

# ── App Growth / ASO / UA ──────────────────────────────────────────────────────
run_channel "AppMasters"          "https://www.youtube.com/@appmasters/videos"
run_channel "Phiture"             "https://www.youtube.com/@phiture/videos"
run_channel "Kosta Eleftheriou"   "https://www.youtube.com/@kostelef/videos"
run_channel "Miki Szeles"         "https://www.youtube.com/@mikiszeles/videos"
run_channel "Adam Lyttle"         "https://www.youtube.com/@adamlyttleapps/videos"
run_channel "Steven Cravotta"     "https://www.youtube.com/@stevencravotta/videos"
run_channel "Melvin Zammit"       "https://www.youtube.com/@melvinzammit/videos"
run_channel "Caden Thompson"      "https://www.youtube.com/@CadenThompson-marketing/videos"
run_channel "Peter Yang"          "https://www.youtube.com/@PeterYangYT/videos"
run_channel "Darius Mora"         "https://www.youtube.com/@DariusMora/videos"
run_channel "Starter Story Build" "https://www.youtube.com/@StarterStoryBuild/videos"
run_channel "Tim Gabe"            "https://www.youtube.com/@TimGabe/videos"
# ── Indie App Founders / Growth Stories ───────────────────────────────────────
run_channel "Marc Lou"            "https://www.youtube.com/@marclou/videos"
run_channel "Pieter Levels"       "https://www.youtube.com/@levelsio/videos"
run_channel "Starter Story"       "https://www.youtube.com/@starterstory/videos"
run_channel "Failory"             "https://www.youtube.com/@failory/videos"

echo ""
echo "All channels processed. CSVs saved to: $OUTPUT_DIR"
