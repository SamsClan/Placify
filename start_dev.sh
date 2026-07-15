set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/.dev-pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✔${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✘${NC} $1"; }


port_in_use() {
  lsof -i ":$1" -sTCP:LISTEN -t >/dev/null 2>&1
}

stop_pidfile() {
  local pidfile="$1"
  if [ -f "$pidfile" ]; then
    local pid
    pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
    rm -f "$pidfile"
  fi
}

start_bg() {
  # $1 = name, $2 = pidfile, $3 = logfile, rest = command
  local name="$1" pidfile="$2" logfile="$3"; shift 3
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    ok "$name already running (pid $(cat "$pidfile")) — leaving it as is"
    return 0
  fi
  rm -f "$pidfile"
  nohup "$@" >"$logfile" 2>&1 &
  local pid=$!
  echo "$pid" > "$pidfile"
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    ok "$name started (pid $pid) — log: $logfile"
  else
    fail "$name failed to start — check $logfile"
  fi
}

wait_for_port() {
  local port="$1" name="$2" timeout="${3:-20}"
  local waited=0
  while ! port_in_use "$port"; do
    if (( waited >= timeout )); then
      fail "$name did not become ready on :$port within ${timeout}s"
      return 1
    fi
    sleep 1
    waited=$((waited + 1))
  done
  ok "$name ready on :$port"
}

wait_for_celery_worker() {
  local timeout="${1:-20}"
  local waited=0
  while (( waited < timeout )); do
    if celery -A backend.celery_entrypoint inspect ping >/dev/null 2>&1; then
      ok "Celery worker is responding"
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done
  fail "Celery worker did not become ready within ${timeout}s"
  return 1
}

# ---------------------------------------------------------------------------
# 1. Redis
# ---------------------------------------------------------------------------
if port_in_use 6379; then
  ok "Redis already running on :6379 — leaving it as is"
elif command -v redis-server >/dev/null 2>&1; then
  start_bg "Redis" "$PID_DIR/redis.pid" "$LOG_DIR/redis.log" redis-server
  wait_for_port 6379 "Redis" 10 || exit 1
else
  fail "redis-server not found. Install it first: brew install redis"
  echo "    Skipping Redis — reminder/report jobs will fail to queue until it's running."
fi

# ---------------------------------------------------------------------------
# 2. Mailpit
# ---------------------------------------------------------------------------
if port_in_use 8025; then
  ok "Mailpit already running (inbox at http://localhost:8025) — leaving it as is"
elif command -v mailpit >/dev/null 2>&1; then
  start_bg "Mailpit" "$PID_DIR/mailpit.pid" "$LOG_DIR/mailpit.log" mailpit
else
  fail "mailpit not found. Install it first: brew install mailpit"
  echo "    Skipping Mailpit — emails will fail to send (jobs still complete, per-recipient failures are logged)."
fi

# ---------------------------------------------------------------------------
# 3. Python virtualenv check
# ---------------------------------------------------------------------------
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
  fail ".venv not found at $PROJECT_ROOT/.venv"
  echo "    Run this first:  python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
  exit 1
fi
# shellcheck disable=SC1091
source "$PROJECT_ROOT/.venv/bin/activate"

# ---------------------------------------------------------------------------
# 4. Celery worker
# ---------------------------------------------------------------------------
stop_pidfile "$PID_DIR/worker.pid"
start_bg "Celery worker" "$PID_DIR/worker.pid" "$LOG_DIR/worker.log" \
  celery -A backend.celery_entrypoint worker --loglevel=info
wait_for_celery_worker 20 || exit 1

# ---------------------------------------------------------------------------
# 5. Backend (Flask)
# ---------------------------------------------------------------------------
stop_pidfile "$PID_DIR/backend.pid"
if port_in_use 5001; then
  ok "Backend port 5001 is now free; starting a fresh backend process"
fi
start_bg "Backend" "$PID_DIR/backend.pid" "$LOG_DIR/backend.log" \
  env PORT=5001 python backend/run.py

# ---------------------------------------------------------------------------
# 6. Celery beat (scheduled daily/monthly triggers — optional but harmless)
# ---------------------------------------------------------------------------
stop_pidfile "$PID_DIR/beat.pid"
start_bg "Celery beat" "$PID_DIR/beat.pid" "$LOG_DIR/beat.log" \
  celery -A backend.celery_entrypoint beat --loglevel=info

echo ""
echo "----------------------------------------------------------------------"
ok "Dev services are up. Frontend is NOT started by this script — run separately:"
echo "    cd frontend && npm run dev"
echo ""
echo "  Mailpit inbox:  http://localhost:8025"
echo "  Backend:        http://127.0.0.1:5001"
echo "  Logs:           $LOG_DIR/"
echo ""
echo "  Sanity check Redis is actually accepting connections:"
echo "    redis-cli ping        # should print PONG"
echo ""
echo "  Stop everything this script started:"
echo "    ./stop_dev.sh"
echo "----------------------------------------------------------------------"
