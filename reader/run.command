#!/bin/bash
# Double-click this file to open the Ethiopian Bible reader in your browser.
cd "$(dirname "$0")" || exit 1
PORT=8123
echo "Serving $(pwd) at http://localhost:$PORT"
echo "Press Ctrl+C to stop."
( sleep 1; open "http://localhost:$PORT/" ) &
exec python3 -m http.server "$PORT"
