#!/usr/bin/env sh
set -eu

# Run migrations (safe to call if already up-to-date).
echo "[entrypoint] Running migrations..." >&2
flask db upgrade

echo "[entrypoint] Starting app..." >&2
python app.py

