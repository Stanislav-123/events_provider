#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"

echo "Running database migrations..."
for attempt in $(seq 1 30); do
  if uv run alembic upgrade head; then
    echo "Migrations applied successfully"
    break
  fi
  if [ "${attempt}" -eq 30 ]; then
    echo "Migrations failed after ${attempt} attempts" >&2
    exit 1
  fi
  echo "Migration attempt ${attempt} failed; retrying in 2s..."
  sleep 2
done

echo "Starting uvicorn on 0.0.0.0:${PORT}"
exec uv run uvicorn main:app --host 0.0.0.0 --port "${PORT}"
