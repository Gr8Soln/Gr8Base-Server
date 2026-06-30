#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_ok() {
    echo -e "${GREEN}$1${NC}"
}

log_warn() {
    echo -e "${YELLOW}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

log_info "Starting Gr8Base backend development services..."

# Resolve a working Python binary.
# On Windows, 'python3' is absent and 'python' may be the MS Store stub
# (App Execution Alias) which exits non-zero on --version.  Try candidates
# in order: python3 → py (Windows Launcher) → python.
PYTHON_BIN=""
for _candidate in python3 py python; do
    if command -v "$_candidate" >/dev/null 2>&1; then
        # Make sure it actually runs (rules out the MS Store stub)
        if "$_candidate" --version >/dev/null 2>&1; then
            PYTHON_BIN="$_candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    log_error "Python is not installed or not on PATH."
    log_warn "On Windows, install Python from https://python.org and ensure 'py' or 'python' is on PATH."
    log_warn "Also disable 'App Execution Aliases' for python.exe in Settings > Apps > Advanced app settings."
    exit 1
fi
log_ok "Using Python binary: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# Use standard .venv path
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "No $VENV_DIR found. Creating virtual environment..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    log_ok "Created $VENV_DIR"
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    log_error "Unable to find activation script for $VENV_DIR"
    exit 1
fi

log_ok "Activated virtual environment ($VENV_DIR)"

# Check if we should use pip or if we have a lockfile format
# Project uses pyproject.toml but we check for requirements.txt for backward compatibility
if [ -f "requirements.txt" ]; then
    REQ_STAMP="$VENV_DIR/.requirements.installed"
    if [ ! -f "$REQ_STAMP" ] || [ "requirements.txt" -nt "$REQ_STAMP" ] || [ "pyproject.toml" -nt "$REQ_STAMP" ]; then
        log_info "Installing/updating dependencies..."
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        # If pyproject.toml exists and has [project] we might want to install in editable mode
        if [ -f "pyproject.toml" ]; then
            python -m pip install -e .
        fi
        touch "$REQ_STAMP"
        log_ok "Dependencies installed"
    else
        log_ok "Dependencies already up-to-date"
    fi
elif [ -f "pyproject.toml" ]; then
    log_info "Installing dependencies from pyproject.toml..."
    python -m pip install --upgrade pip
    python -m pip install -e .
    log_ok "Dependencies installed"
fi

if [ -f ".env" ]; then
    # Use a safer way to export variables that handles spaces and Windows line endings
    log_info "Loading environment variables from .env..."
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Strip all whitespace and potential Windows \r from key
        key=$(echo "$key" | tr -d '[:space:]' | tr -d '\r')
        # Skip comments, empty lines or invalid keys
        [[ $key =~ ^#.*$ ]] || [[ -z $key ]] && continue
        
        # Strip potential Windows \r, surrounding whitespace, and optional wrapping quotes
        value=$(echo "$value" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        
        export "$key=$value"
    done < .env
    log_ok "Loaded environment variables from .env"
elif [ -f ".env.sample" ]; then
    log_warn "Notice: .env not found. Creating from .env.sample..."
    cp .env.sample .env
    log_warn "Please review .env and restart if necessary."
fi

if [ -f "alembic.ini" ]; then
    log_info "Running database migrations (GR8BASE schema)..."
    if MIGRATION_OUTPUT=$(python -m alembic upgrade head 2>&1); then
        [ -n "$MIGRATION_OUTPUT" ] && echo "$MIGRATION_OUTPUT"
        log_ok "Migrations complete"
    else
        echo "$MIGRATION_OUTPUT"
        if echo "$MIGRATION_OUTPUT" | grep -qi "password authentication failed"; then
            log_error "Database authentication failed while running migrations."
            log_warn "Update DATABASE_URL in .env with valid PostgreSQL credentials."
            log_info "Current DATABASE_URL target (password hidden):"
            python - <<'PY'
from urllib.parse import urlparse
import os

url = os.getenv("DATABASE_URL", "")
if not url:
    print("  DATABASE_URL is not set")
else:
    parsed = urlparse(url)
    user = parsed.username or "<none>"
    host = parsed.hostname or "<none>"
    port = parsed.port or "<default>"
    db_name = (parsed.path or "/").lstrip("/") or "<none>"
    print(f"  user={user} host={host} port={port} db={db_name}")
    print("  Tip: URL-encode special characters in password (example: @ -> %40).")
PY
        fi
        exit 1
    fi
else
    log_warn "alembic.ini not found, skipping migration check"
fi

# Optional first-admin bootstrap for local/dev use.
if [ "${RUN_SUPER_ACCOUNT_SETUP_ON_START:-true}" = "true" ]; then
    if [ -n "${SUPER_EMAIL:-}" ]; then
        log_info "Running super account setup script..."
        python -m scripts.setup_super_account
        log_ok "Super account setup completed"
    else
        log_warn "RUN_SUPER_ACCOUNT_SETUP_ON_START=true but SUPER_EMAIL is empty; skipping"
    fi
fi


# Worker check for Celery (notification system)
CELERY_APP="app.core.config.celery_config:celery_app" 
CELERY_WORKER_ARGS="--loglevel=info --concurrency=4"

case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*)
        CELERY_WORKER_ARGS="--pool=solo --loglevel=info"
        log_info "Windows environment: Celery worker using solo pool"
        ;;
esac

# Start Celery worker and beat scheduler for scheduled notifications
if python -c "from app.core.config.celery_config import celery_app; from celery.bin import worker" 2>/dev/null; then
    log_info "Starting Celery worker and beat scheduler..."
    
    # Kill any existing celery processes
    pkill -f "celery -A app.core.config.celery_config worker" >/dev/null 2>&1 || true
    pkill -f "celery -A app.core.config.celery_config beat" >/dev/null 2>&1 || true
    
    # Start worker in background
    nohup celery -A app.core.config.celery_config worker ${CELERY_WORKER_ARGS} > logs/celery_worker.log 2>&1 &
    WORKER_PID=$!
    
    # Start beat scheduler in background
    nohup celery -A app.core.config.celery_config beat --loglevel=info > logs/celery_beat.log 2>&1 &
    BEAT_PID=$!
    
    log_ok "Celery worker (PID: $WORKER_PID) and beat scheduler (PID: $BEAT_PID) started"
    log_info "View worker logs: tail -f logs/celery_worker.log"
    log_info "View beat logs: tail -f logs/celery_beat.log"
else
    log_warn "Celery not available."
fi

PORT=${PORT:-9001}
log_ok "Starting Uvicorn for gr8base-server on port ${PORT}"
log_info "API Documentation: http://localhost:${PORT}/api/v1/docs"

# Parse CLI args so callers can do: ./start.sh --reload false
# Supported forms: --reload false | --reload=false | --no-reload
RELOAD=true
UVICORN_EXTRA=""
while (( "$#" )); do
    case "$1" in
        --reload)
            if [ -n "$2" ]; then
                RELOAD="$2"
                shift 2
            else
                RELOAD=true
                shift
            fi
            ;;
        --reload=*)
            RELOAD="${1#*=}"
            shift
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        --port)
            if [ -n "$2" ]; then
                PORT="$2"
                shift 2
            else
                shift
            fi
            ;;
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--reload true|false] [--port PORT] [uvicorn args...]"
            exit 0
            ;;
        *)
            UVICORN_EXTRA="$UVICORN_EXTRA $1"
            shift
            ;;
    esac
done

# Normalize RELOAD bool
RELOAD_LOWER=$(echo "$RELOAD" | tr '[:upper:]' '[:lower:]')
RELOAD_FLAG=""
case "$RELOAD_LOWER" in
    false|0|no|n)
        RELOAD_FLAG=""
        ;;
    *)
        RELOAD_FLAG="--reload"
        ;;
esac

# Start the app.main:app (which uses create_app() bootstrap)
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" $RELOAD_FLAG $UVICORN_EXTRA
