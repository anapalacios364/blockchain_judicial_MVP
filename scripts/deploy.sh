#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/docker"

if [ ! -f "$ROOT_DIR/.env" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "Se creó .env desde .env.example. Ajusta las variables antes de continuar."
fi

docker compose --env-file ../.env up --build -d
echo "Stack levantado en http://localhost:8069"
echo "Prometheus en http://localhost:9090"
