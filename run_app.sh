#!/bin/bash

# Simple Auto Environment Runner
# Usage: ./run_app.sh [env_file] [command]
# Example: ./run_app.sh .env "python app/main.py"

ENV_FILE="${1:-.env}"
CMD="${2:-uvicorn app.main:app --reload --host 0.0.0.0 --port 8000}"

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found"
    exit 1
fi

echo "Loading $ENV_FILE and running: $CMD"

# Load env vars, run command, then cleanup
(
    set -a  # Auto-export all variables
    source "$ENV_FILE"
    set +a

    echo "Environment loaded. Starting app..."
    $CMD
    # uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
)

echo "App finished. Environment cleaned up."
