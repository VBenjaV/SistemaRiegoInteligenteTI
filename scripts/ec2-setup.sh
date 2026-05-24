#!/usr/bin/env bash
# Instalación inicial en EC2 (Ubuntu 22.04/24.04 o Debian)
# Ejecutar como usuario con sudo: bash scripts/ec2-setup.sh

set -euo pipefail

if ! command -v sudo >/dev/null 2>&1; then
  echo "Este script requiere sudo."
  exit 1
fi

echo "==> Actualizando paquetes..."
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

echo "==> Instalando dependencias..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  ca-certificates curl git gnupg ufw

echo "==> Instalando Docker..."
if ! command -v docker >/dev/null 2>&1; then
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${VERSION_CODENAME:-$VERSION_ID}") stable" |
    sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

echo "==> Agregando usuario actual al grupo docker..."
sudo usermod -aG docker "$USER" || true

echo "==> Configurando firewall (UFW)..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo ""
echo "Listo. Cierra sesión SSH y vuelve a entrar (o ejecuta: newgrp docker)"
echo "Luego clona el repo, configura backend/.env e IotCore/, y ejecuta:"
echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
