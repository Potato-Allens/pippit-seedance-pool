#!/usr/bin/env bash
# Minimal curl loop against the pool gateway.
set -euo pipefail
BASE=${BASE:-http://127.0.0.1:8788}
KEY=${KEY:?set KEY=sk-wz-...}
PROMPT=${PROMPT:-"a rainy neon street at midnight, slow dolly, cinematic"}

JOB=$(curl -s -X POST "$BASE/v1/videos" \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d "{\"model\":\"seedance-2.5-720p-natural\",\"prompt\":\"$PROMPT\",\"seconds\":15,\"ratio\":\"9:16\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
echo "job=$JOB"

while :; do
  BODY=$(curl -s -H "Authorization: Bearer $KEY" "$BASE/v1/videos/$JOB")
  STATUS=$(printf '%s' "$BODY" | python3 -c 'import sys,json;print(json.load(sys.stdin)["status"])')
  echo "  $STATUS"
  [ "$STATUS" = "completed" ] && break
  [ "$STATUS" = "failed" ] && { echo "$BODY"; exit 1; }
  sleep 10
done

curl -s -H "Authorization: Bearer $KEY" -o out.mp4 "$BASE/v1/videos/$JOB/content"
echo "saved out.mp4 ($(wc -c < out.mp4) bytes)"
