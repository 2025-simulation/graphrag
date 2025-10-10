#!/bin/sh

echo "[STARTUP] apt updating..."
apt update

echo "[STARTUP] installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "[STARTUP] setting up the uv environment..."
uv venv --python 3.12 && /app/graphrag/.venv/python -m pip install -r requirements.txt
