#!/usr/bin/env bash
# stop_dev.sh — stop everything start_dev.sh started (by pid file).
# Services that were already running before start_dev.sh (and so were left
# alone) are also left alone here.

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$PROJECT_ROOT/.dev-pids"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✔${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

if [ ! -d "$PID_DIR" ]; then
  warn "No .dev-pids directory found — nothing to stop."
  exit 0
fi

stop_pid_file() {
  local pidfile="$1"
  local name="$(basename "$pidfile" .pid)"
  local pid=""

  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile")"
  fi

  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    ok "Stopped $name (pid $pid)"
  else
    warn "$name was already stopped"
  fi

  rm -f "$pidfile"
}

for pidfile in "$PID_DIR"/*.pid; do
  [ -e "$pidfile" ] || continue
  stop_pid_file "$pidfile"
done

for proc_name in backend celery mailpit redis-server; do
  pids="$(ps -ef | awk -v name="$proc_name" '$0 ~ name && $0 !~ /awk/ {print $2}' | tr '\n' ' ' | sed 's/ $//')"
  if [ -n "$pids" ]; then
    for pid in $pids; do
      if ps -p "$pid" >/dev/null 2>&1; then
        kill "$pid" 2>/dev/null || true
      fi
    done
  fi
done

ok "Done. (Redis/Mailpit left running if they were already up before start_dev.sh.)"
