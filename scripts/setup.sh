#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Setup complete"
echo "Run locally: docker compose up --build"
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Setup complete. Run: docker compose -f docker/docker-compose.yml up --build"
