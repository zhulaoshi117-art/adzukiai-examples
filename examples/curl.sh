#!/usr/bin/env bash
# Raw HTTP, no SDK. Useful when you need to see exactly what goes over the wire.
#
#   export ADZUKI_API_KEY="sk-..."
#   bash examples/curl.sh
#
# Add -D - before the URL to see the response headers, and -N to disable
# buffering when you add "stream": true to the body.
set -euo pipefail

: "${ADZUKI_API_KEY:?set ADZUKI_API_KEY first (https://adzukiai.com -> API keys)}"
BASE="${ADZUKI_BASE_URL:-https://adzukiai.com/v1}"
MODEL="${ADZUKI_MODEL:-deepseek-v4.1-flash}"

curl -sS "$BASE/chat/completions" \
  -H "Authorization: Bearer $ADZUKI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Explain B-tree splits\"}]
  }"
echo
