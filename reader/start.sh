#!/bin/bash
# ---------------------------------------------------------------
#  Ethiopian Bible Reader - full launcher
#  Starts: static web server (8123), Piper TTS server (8124),
#          and two public tunnels. Prints the public link.
#
#  Usage:  ./start.sh          (local only, opens browser)
#          ./start.sh public   (also creates public tunnels)
# ---------------------------------------------------------------
cd "$(dirname "$0")" || exit 1
DIR="$(pwd)"
LOG="$DIR/.logs"
mkdir -p "$LOG"

WEB_PORT=8123
PIPER_PORT=8124
PUBLIC="${1:-local}"

PY_BIN="$(command -v python3 || echo /usr/bin/python3)"

say()  { printf "\033[1;36m%s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m%s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m%s\033[0m\n" "$*"; }

# --- stop any previous run -------------------------------------
stop_old() {
  pkill -f "http.server $WEB_PORT"       2>/dev/null
  pkill -f "piper_server.py"             2>/dev/null
  pkill -f "localhost.run"               2>/dev/null
  pkill -f "serveo.net"                  2>/dev/null
  sleep 1
}
stop_old

# --- start static web server -----------------------------------
say "Starting web server on $WEB_PORT ..."
nohup "$PY_BIN" -m http.server "$WEB_PORT" > "$LOG/web.log" 2>&1 &
WEB_PID=$!
echo "  web pid $WEB_PID"

# --- start Piper TTS server ------------------------------------
if [ -f "$DIR/piper_server.py" ] && [ -d "$DIR/tts_voices" ]; then
  say "Starting Piper TTS server on $PIPER_PORT ..."
  nohup "$PY_BIN" "$DIR/piper_server.py" "$PIPER_PORT" > "$LOG/piper.log" 2>&1 &
  PIPER_PID=$!
  echo "  piper pid $PIPER_PID"
else
  warn "piper_server.py or tts_voices/ missing - skipping TTS server"
  PIPER_PID=""
fi

# --- wait for local servers to come up -------------------------
sleep 3
if ! curl -s -o /dev/null "http://127.0.0.1:$WEB_PORT/index.html"; then
  warn "web server not responding yet, waiting..."
  sleep 3
fi
ok "Local reader:  http://localhost:$WEB_PORT/"

if [ -n "$PIPER_PID" ]; then
  if curl -s -o /dev/null "http://127.0.0.1:$PIPER_PORT/piper/voices"; then
    ok "Local TTS:     http://127.0.0.1:$PIPER_PORT/piper/voices"
  else
    warn "Piper server not responding yet"
  fi
fi

# --- public tunnels --------------------------------------------
if [ "$PUBLIC" = "public" ]; then
  say "Opening public tunnels (localhost.run) ..."

  nohup ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 \
        -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
        -R 80:localhost:$WEB_PORT nokey@localhost.run \
        > "$LOG/tun_web.log" 2>&1 &
  nohup ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 \
        -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
        -R 80:localhost:$PIPER_PORT nokey@localhost.run \
        > "$LOG/tun_piper.log" 2>&1 &

  say "Waiting for tunnel URLs (up to 40s) ..."
  WEB_URL=""; PIPER_URL=""
  for i in $(seq 1 40); do
    [ -z "$WEB_URL" ]   && WEB_URL="$(grep -oE 'https://[a-z0-9]+\.lhr\.life' "$LOG/tun_web.log"   2>/dev/null | head -1)"
    [ -z "$PIPER_URL" ] && PIPER_URL="$(grep -oE 'https://[a-z0-9]+\.lhr\.life' "$LOG/tun_piper.log" 2>/dev/null | head -1)"
    [ -n "$WEB_URL" ] && [ -n "$PIPER_URL" ] && break
    sleep 1
  done

  echo
  if [ -n "$WEB_URL" ] && [ -n "$PIPER_URL" ]; then
    ok "======================================================"
    ok " PUBLIC LINK (share this):"
    ok " $WEB_URL/?piper=$PIPER_URL"
    ok "======================================================"
    echo
    echo " Reader:  $WEB_URL"
    echo " TTS:     $PIPER_URL"
    echo
    echo " (Only works while this Mac is on and these processes run.)"
    echo "$WEB_URL/?piper=$PIPER_URL" > "$DIR/.public_link.txt"
    echo " Link saved to .public_link.txt"
  else
    warn "Could not get tunnel URLs. Check $LOG/tun_web.log and $LOG/tun_piper.log"
  fi
else
  echo
  ok "Local:  http://localhost:$WEB_PORT/"
  echo " For a public link, run:   ./start.sh public"
fi

echo
echo "Logs in: $LOG/"
echo "To stop everything:  pkill -f http.server; pkill -f piper_server.py; pkill -f localhost.run"
