#!/bin/bash
# sweep.sh — drive Chrome through a list of (outbound, return) combos for VA award search.
#
# Inputs (env vars):
#   ORIGIN       e.g. SEA
#   DEST         e.g. LHR
#   COMBOS_FILE  path to a file with one "YYYY-MM-DD YYYY-MM-DD" per line (out, ret)
#   OUT_DIR      where to write per-combo JSON (default /tmp/va_search)
#   PAX          passenger string (default a1t0c0i0 = 1 adult)
#
# Reads parse.js from the same directory as this script.
# Prints one progress line per combo.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSE_JS_FILE="${SCRIPT_DIR}/parse.js"
OUT_DIR="${OUT_DIR:-$HOME/va-reward-reports}"
PAX="${PAX:-a2t0c0i0}"  # default 2 adults (override: PAX=a1t0c0i0 for solo)

: "${ORIGIN:?ORIGIN env var required (e.g. SEA)}"
: "${DEST:?DEST env var required (e.g. LHR)}"
: "${COMBOS_FILE:?COMBOS_FILE env var required}"
[ -f "$PARSE_JS_FILE" ] || { echo "missing $PARSE_JS_FILE"; exit 1; }
[ -f "$COMBOS_FILE" ] || { echo "missing $COMBOS_FILE"; exit 1; }
mkdir -p "$OUT_DIR"

JS=$(python3 -c "import json,sys; print(json.dumps(open('$PARSE_JS_FILE').read(), ensure_ascii=False))")

count=0
total=$(wc -l <"$COMBOS_FILE" | tr -d ' ')
while read -r OUT_DATE RET_DATE; do
  [ -z "$OUT_DATE" ] && continue
  count=$((count+1))
  OUTFILE="${OUT_DIR}/combo_${OUT_DATE}_${RET_DATE}.json"
  URL="https://www.virginatlantic.com/en-US/flights/search/slice?passengers=${PAX}&origin=${ORIGIN}&origin=${DEST}&awardSearch=true&destination=${DEST}&destination=${ORIGIN}&departing=${OUT_DATE}&departing=${RET_DATE}"
  osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"${URL}\"" >/dev/null
  sleep 10
  CUR=$(osascript -e 'tell application "Google Chrome" to return URL of active tab of front window')
  if [[ "$CUR" == *"identity.virginatlantic.com"* ]]; then
    echo "[$count/$total] ${OUT_DATE} -> ${RET_DATE}: LOGIN_REQUIRED"
    echo '{"err":"login_required","url":"'"$CUR"'"}' > "$OUTFILE"
    continue
  fi
  RESULT=$(osascript -e "tell application \"Google Chrome\"" -e "set js to ${JS}" -e "execute front window's active tab javascript js" -e "end tell")
  echo "$RESULT" > "$OUTFILE"
  PRICE=$(echo "$RESULT" | python3 -c "
import json,sys
try:
  j=json.loads(sys.stdin.read())
  cs=j.get('cabins',[])
  if cs:
    eco=next((c for c in cs if 'Economy' in c['cabin']), cs[0])
    print(f\"{eco['cabin']}: {eco['pts']:,} + US\${eco['tax']}\")
  else: print('NO_RESULTS')
except Exception as e: print('ERR',e)
")
  echo "[$count/$total] ${OUT_DATE} -> ${RET_DATE}: ${PRICE}"
done <"$COMBOS_FILE"
echo "DONE — output in ${OUT_DIR}"
