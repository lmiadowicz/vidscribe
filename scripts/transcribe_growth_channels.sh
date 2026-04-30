#!/usr/bin/env bash
# Transcribes recent videos from mobile growth / app founder YouTube channels.
# Run: bash scripts/transcribe_growth_channels.sh
# Adjust --limit and --model to your needs.

set -euo pipefail

MODEL="${MODEL:-base}"        # override: MODEL=small bash ...
LIMIT="${LIMIT:-}"            # override: LIMIT=50 bash ... (empty = all videos)
OUTPUT_DIR="${OUTPUT_DIR:-./channel_transcriptions}"
USE_MLX="${USE_MLX:-}"        # set USE_MLX=1 to enable Apple Silicon acceleration
SINCE="${SINCE:-$(date -v-2y -v-6m +%Y-%m-%d)}"  # override: SINCE=2024-01-01 bash ... (only videos on/after date)
COOKIES_FROM_BROWSER="${COOKIES_FROM_BROWSER:-}"  # override: COOKIES_FROM_BROWSER=chrome bash ... (safari doesn't work on macOS due to App Sandbox)

mkdir -p "$OUTPUT_DIR"

run_channel() {
  local name="$1"
  local url="$2"
  local slug
  slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
  local output="$OUTPUT_DIR/${slug}.csv"

  echo ""
  echo ">>> [$name] $url"
  echo "    Output: $output"

  local mlx_flag=""
  [[ -n "$USE_MLX" ]] && mlx_flag="--use-mlx"
  local limit_flag=""
  [[ -n "$LIMIT" ]] && limit_flag="--limit $LIMIT"
  local since_flag=""
  [[ -n "$SINCE" ]] && since_flag="--since $SINCE"
  local cookies_flag=""
  [[ -n "$COOKIES_FROM_BROWSER" ]] && cookies_flag="--cookies-from-browser $COOKIES_FROM_BROWSER"

  if vidscribe playlist "$url" \
    --output "$output" \
    --model "$MODEL" \
    $limit_flag \
    $since_flag \
    $mlx_flag \
    $cookies_flag; then
    echo "    Done: $output"
  else
    echo "    SKIPPED: $name failed (channel may not exist or is unavailable)"
  fi
}

run_channel "Greg Isenberg"       "https://www.youtube.com/@GregIsenberg/videos"
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
run_channel "Failory"             "https://www.youtube.com/@failory/videos"

echo ""
echo "All channels processed. CSVs saved to: $OUTPUT_DIR"
