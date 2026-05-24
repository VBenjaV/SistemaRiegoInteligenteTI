#!/usr/bin/env bash
# Actualizar y levantar stack de producción (desde la raíz del repo)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f backend/.env ]]; then
  echo "Falta backend/.env. Copia backend/.env.example y complétalo."
  exit 1
fi

if [[ ! -f IotCore/AmazonRootCA1.pem ]]; then
  echo "Faltan certificados en IotCore/. Copia los archivos AWS IoT al servidor."
  exit 1
fi

BRANCH="${GIT_BRANCH:-DeployAWS}"
echo "==> Actualizar rama ${BRANCH}..."
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "==> Build y arranque..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo ""
echo "==> Estado:"
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

PUBLIC_IP="${PUBLIC_IP:-}"
if [[ -z "$PUBLIC_IP" ]] && command -v curl >/dev/null 2>&1; then
  PUBLIC_IP="$(curl -fsS --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)"
fi

echo ""
if [[ -n "$PUBLIC_IP" ]]; then
  echo "Dashboard: http://${PUBLIC_IP}/"
  echo "API docs:  http://${PUBLIC_IP}/docs"
else
  echo "Dashboard: http://<IP_PUBLICA_EC2>/"
fi
echo "Health:    curl http://localhost/health"
