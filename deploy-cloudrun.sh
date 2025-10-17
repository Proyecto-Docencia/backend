#!/bin/bash
# Script de despliegue rápido para Cloud Run (sin Cloud Build)

# Configuración
PROJECT_ID="gen-lang-client-0776831973"
SERVICE_NAME="backend-django"
REGION="us-central1"
CLOUDSQL_INSTANCE="gen-lang-client-0776831973:us-central1:admin123"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Despliegue de Backend Django a Cloud Run ===${NC}"

# 1. Construir imagen localmente
echo -e "${YELLOW}[1/4] Construyendo imagen Docker...${NC}"
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al construir la imagen${NC}"
    exit 1
fi

# 2. Subir a Google Container Registry
echo -e "${YELLOW}[2/4] Subiendo imagen a GCR...${NC}"
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al subir la imagen${NC}"
    exit 1
fi

# 3. Desplegar a Cloud Run
echo -e "${YELLOW}[3/4] Desplegando a Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --timeout 600s \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --add-cloudsql-instances $CLOUDSQL_INSTANCE \
    --set-env-vars "PORT=8080,\
DJANGO_SECRET_KEY=mi-secret-key-super-segura-para-produccion-2024,\
DJANGO_DEBUG=0,\
DJANGO_ALLOWED_HOSTS=*.run.app,.run.app,\
DB_ENGINE=mysql,\
DB_HOST=/cloudsql/$CLOUDSQL_INSTANCE,\
DB_PORT=3306,\
DB_NAME=admin123,\
DB_USER=admin123,\
DB_PASSWORD=tuchangoGG123#,\
CORS_ALLOW_ALL_ORIGINS=1,\
CSRF_TRUSTED_ORIGINS=https://*.run.app,\
ENABLE_RAG=0,\
SKIP_DB_WAIT=0"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al desplegar${NC}"
    exit 1
fi

# 4. Obtener URL
echo -e "${YELLOW}[4/4] Obteniendo URL del servicio...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✓ Despliegue completado exitosamente${NC}"
echo -e "${GREEN}URL del servicio: $SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}Prueba el servicio:${NC}"
echo "curl $SERVICE_URL/api/v1/health/"
