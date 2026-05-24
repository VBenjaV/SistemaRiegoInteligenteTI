# Levanta todo el stack (build + healthchecks)
param(
    [switch]$Dev
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot ..

if ($Dev) {
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
} else {
    docker compose up -d --build
}

Write-Host ""
Write-Host "Esperando servicios..." -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "Dashboard:  http://localhost:5173" -ForegroundColor Green
Write-Host "API Docs:   http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health:     http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Logs: docker compose logs -f" -ForegroundColor Yellow
