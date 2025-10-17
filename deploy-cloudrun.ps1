#!/bin/bash
# deploy-cloudrun.ps1 - Version para PowerShell
# Script de despliegue rápido para Cloud Run (sin Cloud Build)

# Configuración
$PROJECT_ID = "gen-lang-client-0776831973"
$SERVICE_NAME = "backend-django"
$REGION = "us-central1"
$CLOUDSQL_INSTANCE = "gen-lang-client-0776831973:us-central1:admin123"

Write-Host "=== Despliegue de Backend Django a Cloud Run ===" -ForegroundColor Green

# 1. Construir imagen localmente
Write-Host "[1/4] Construyendo imagen Docker..." -ForegroundColor Yellow
docker build -t "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al construir la imagen" -ForegroundColor Red
    exit 1
}

# 2. Subir a Google Container Registry
Write-Host "[2/4] Subiendo imagen a GCR..." -ForegroundColor Yellow
docker push "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al subir la imagen" -ForegroundColor Red
    exit 1
}

# 3. Desplegar a Cloud Run
Write-Host "[3/4] Desplegando a Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --timeout 600s `
    --memory 2Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --add-cloudsql-instances $CLOUDSQL_INSTANCE `
    --set-env-vars "PORT=8080,DJANGO_SECRET_KEY=mi-secret-key-super-segura-para-produccion-2024,DJANGO_DEBUG=0,DJANGO_ALLOWED_HOSTS=*.run.app,.run.app,DB_ENGINE=mysql,DB_HOST=/cloudsql/$CLOUDSQL_INSTANCE,DB_PORT=3306,DB_NAME=admin123,DB_USER=admin123,DB_PASSWORD=tuchangoGG123#,CORS_ALLOW_ALL_ORIGINS=1,CSRF_TRUSTED_ORIGINS=https://*.run.app,ENABLE_RAG=0,SKIP_DB_WAIT=0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al desplegar" -ForegroundColor Red
    exit 1
}

# 4. Obtener URL
Write-Host "[4/4] Obteniendo URL del servicio..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'

Write-Host "`n✓ Despliegue completado exitosamente" -ForegroundColor Green
Write-Host "URL del servicio: $SERVICE_URL" -ForegroundColor Green
Write-Host "`nPrueba el servicio:" -ForegroundColor Yellow
Write-Host "curl $SERVICE_URL/api/v1/health/"
Write-Host "curl $SERVICE_URL/healthz"
