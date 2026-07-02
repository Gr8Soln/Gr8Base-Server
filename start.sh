#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}$1${NC}"; }
log_ok()    { echo -e "${GREEN}$1${NC}"; }
log_warn()  { echo -e "${YELLOW}$1${NC}"; }
log_error() { echo -e "${RED}$1${NC}"; }

log_info "Starting Gr8Base backend development services..."

# ── Resolve Python binary ──────────────────────────────────────────────────────
# On Windows, 'python3' is absent and 'python' may be the MS Store stub.
# uv bundles its own Python, so we only need uv on PATH.
PYTHON_BIN=""
for _candidate in python3 py python; do
    if command -v "$_candidate" >/dev/null 2>&1; then
        if "$_candidate" --version >/dev/null 2>&1; then
            PYTHON_BIN="$_candidate"
            break
        fi
    fi
done

if ! command -v uv >/dev/null 2>&1; then
    log_error "uv is not installed."
    log_info "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    log_info "Or on Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    exit 1
fi
log_ok "Using uv ($(uv --version))"

if [ -n "$PYTHON_BIN" ]; then
    log_ok "Using Python binary: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"
fi

# ── Virtual environment ────────────────────────────────────────────────────────
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating virtual environment with uv..."
    uv venv "$VENV_DIR"
    log_ok "Created $VENV_DIR"
fi

# Activate (works on both Unix and Windows Git Bash)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    log_error "Unable to find activation script for $VENV_DIR"
    exit 1
fi
log_ok "Activated virtual environment ($VENV_DIR)"

# ── Install dependencies ──────────────────────────────────────────────────────
log_info "Installing dependencies with uv..."
if uv sync --frozen 2>/dev/null; then
    log_ok "Dependencies installed (uv sync --frozen)"
else
    log_info "No lockfile found — running uv sync (will generate one)..."
    uv sync
    log_ok "Dependencies installed"
fi
log_ok "All dependencies installed"

# ── Environment variables ──────────────────────────────────────────────────────
if [ -f ".env" ]; then
    log_info "Loading environment variables from .env..."
    while IFS='=' read -r key value || [ -n "$key" ]; do
        key=$(echo "$key" | tr -d '[:space:]' | tr -d '\r')
        [[ $key =~ ^#.*$ ]] || [[ -z $key ]] && continue
        value=$(echo "$value" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        export "$key=$value"
    done < .env
    log_ok "Loaded environment variables from .env"
else
    log_warn ".env not found — copying from .env.example..."
    cp .env.example .env 2>/dev/null || log_warn "No .env.example either; skipping"
fi

# ── Alembic migrations ─────────────────────────────────────────────────────────
if [ -f "alembic.ini" ]; then
    log_info "Running database migrations..."
    if MIGRATION_OUTPUT=$(uv run alembic upgrade head 2>&1); then
        [ -n "$MIGRATION_OUTPUT" ] && echo "$MIGRATION_OUTPUT"
        log_ok "Migrations complete"
    else
        echo "$MIGRATION_OUTPUT"
        if echo "$MIGRATION_OUTPUT" | grep -qi "password authentication failed"; then
            log_error "Database authentication failed while running migrations."
            log_warn "Update DATABASE_URL in .env with valid PostgreSQL credentials."
        fi
        if echo "$MIGRATION_OUTPUT" | grep -qi "relation.*does not exist"; then
            log_info "HINT: You can bootstrap the database with:"
            log_info "  uv run alembic upgrade head"
        fi
        exit 1
    fi
else
    log_warn "alembic.ini not found; skipping migrations"
fi

# ── Alembic auto-generation helper (informational) ─────────────────────────────
if [ -n "${AUTOGENERATE_MIGRATION:-}" ] && [ "$AUTOGENERATE_MIGRATION" = "true" ]; then
    log_info "Auto-generating migration from model changes..."
    MIGRATION_MSG="${MIGRATION_MESSAGE:-auto migration}"
    uv run alembic revision --autogenerate -m "$MIGRATION_MSG"
    log_ok "Migration generated. Run again to apply it."
fi

# ── Optional super-account bootstrap ───────────────────────────────────────────
if [ "${RUN_SUPER_ACCOUNT_SETUP_ON_START:-true}" = "true" ]; then
    if [ -n "${SUPER_EMAIL:-}" ]; then
        log_info "Running super account setup script..."
        uv run python -m scripts.setup_super_account 2>/dev/null || log_warn "Super account script not found; skipping"
        log_ok "Super account setup completed"
    else
        log_warn "RUN_SUPER_ACCOUNT_SETUP_ON_START=true but SUPER_EMAIL is empty; skipping"
    fi
fi

# ── Celery worker ──────────────────────────────────────────────────────────────
CELERY_APP="app.infrastructure.queue.celery_config:celery_app"
CELERY_WORKER_ARGS="--loglevel=info --concurrency=4"

case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*)
        CELERY_WORKER_ARGS="--pool=solo --loglevel=info"
        log_info "Windows environment: Celery worker using solo pool"
        ;;
esac

if uv run python -c "from celery import Celery; Celery()" 2>/dev/null; then
    log_info "Starting Celery worker and beat scheduler..."

    pkill -f "celery -A $CELERY_APP worker" 2>/dev/null || true
    pkill -f "celery -A $CELERY_APP beat" 2>/dev/null || true

    mkdir -p logs
    nohup uv run celery -A "$CELERY_APP" worker $CELERY_WORKER_ARGS > logs/celery_worker.log 2>&1 &
    WORKER_PID=$!
    nohup uv run celery -A "$CELERY_APP" beat --loglevel=info > logs/celery_beat.log 2>&1 &
    BEAT_PID=$!

    log_ok "Celery worker (PID: $WORKER_PID) and beat scheduler (PID: $BEAT_PID) started"
    log_info "View worker logs: tail -f logs/celery_worker.log"
else
    log_warn "Celery not available — skipping worker start"
fi

# ── Start Uvicorn ──────────────────────────────────────────────────────────────
PORT=${PORT:-9001}
log_ok "Starting Uvicorn for gr8base-server on port ${PORT}"
log_info "API Documentation: http://localhost:${PORT}/api/v1/docs"
log_info "API Base URL: http://localhost:${PORT}/api/v1/"

# Parse CLI args
RELOAD=true
UVICORN_EXTRA=""
while (( "$#" )); do
    case "$1" in
        --reload)
            if [ -n "$2" ]; then RELOAD="$2"; shift 2; else RELOAD=true; shift; fi ;;
        --reload=*)
            RELOAD="${1#*=}"; shift ;;
        --no-reload)
            RELOAD=false; shift ;;
        --port)
            if [ -n "$2" ]; then PORT="$2"; shift 2; else shift; fi ;;
        --port=*)
            PORT="${1#*=}"; shift ;;
        --help|-h)
            echo "Usage: $0 [--reload true|false] [--port PORT] [uvicorn args...]"
            echo ""
            echo "Environment variables:"
            echo "  AUTOGENERATE_MIGRATION=true   Run 'alembic revision --autogenerate' on start"
            echo "  MIGRATION_MESSAGE=msg          Description for auto-generated migration"
            echo "  PORT=9001                      Uvicorn listen port"
            exit 0
            ;;
        *)
            UVICORN_EXTRA="$UVICORN_EXTRA $1"
            shift ;;
    esac
done

RELOAD_LOWER=$(echo "$RELOAD" | tr '[:upper:]' '[:lower:]')
RELOAD_FLAG=""
case "$RELOAD_LOWER" in
    false|0|no|n) ;;
    *) RELOAD_FLAG="--reload" ;;
esac

# main.py lives in app/ — uvicorn resolves it as app.main:app
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" $RELOAD_FLAG $UVICORN_EXTRA
