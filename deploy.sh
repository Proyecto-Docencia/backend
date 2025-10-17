#!/bin/bash

# Script para desplegar a Google Cloud Run
set -e

# ConfiguraciÃ³n del proyecto
PROJECT_ID="tu-project-id"
SERVICE_NAME="backend-django"
REGION="us-central1"

echo "ðŸš€ Desplegando $SERVICE_NAME a Google Cloud Run..."

# Verificar que estamos autenticados
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "âŒ No estÃ¡s autenticado. Ejecuta: gcloud auth login"
    exit 1
fi

# Configurar el proyecto
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo "ðŸ“¡ Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Construir y desplegar usando Cloud Build
echo "ðŸ”¨ Construyendo y desplegando con Cloud Build..."
gcloud builds submit --config cloudbuild.yaml

# Obtener la URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "âœ… Â¡Despliegue completado!"
echo "ðŸŒ Tu backend estÃ¡ disponible en: $SERVICE_URL"
echo ""
echo "ðŸ“‹ PrÃ³ximos pasos:"
echo "  1. Configura tu base de datos Cloud SQL"
echo "  2. Actualiza las variables de entorno en cloudbuild.yaml"
echo "  3. Configura tu dominio personalizado (opcional)"