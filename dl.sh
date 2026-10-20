#!/bin/bash
cd "$(dirname "$0")"
SEL=/var/folders/6f/rln9mdz94sqg2dq1_zm9hs2w0000gn/T/opencode/sel10.json
OUT=reader/data/manuscripts
mkdir -p "$OUT"
n=$(jq 'length' "$SEL"); saved=0; fail=0
for i in $(seq 0 $((n-1))); do
  url=$(jq -r ".[$i].dl" "$SEL")
  title=$(jq -r ".[$i].title" "$SEL")
  slug=$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//' | cut -c1-70)
  [ -z "$slug" ] && slug="manuscript-$i"
  f="$OUT/$slug.jpg"
  [ -s "$f" ] && { saved=$((saved+1)); continue; }
  code=$(curl -s -L --retry 3 --retry-delay 3 -A "EOTCBibleReader/1.0 (offline educational reader)" -o "$f" -w "%{http_code}" "$url")
  if [ "$code" = "200" ] && [ -s "$f" ]; then saved=$((saved+1)); else rm -f "$f"; fail=$((fail+1)); echo "FAIL[$code] $title"; fi
  sleep 0.4
done
echo "saved=$saved/$n fail=$fail"
