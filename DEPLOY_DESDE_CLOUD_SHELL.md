# Guia Rapida para Desplegar Backend desde Google Cloud Shell

## ✅ Cambios ya subidos al repositorio

El backend esta actualizado en: https://github.com/Proyecto-Docencia/backend
- Rama: **master**
- Commit: "Fix: Backend optimizado para Cloud Run"

---

## 🚀 PASOS PARA DESPLEGAR (Google Cloud Shell)

### 1. Abrir Google Cloud Shell
Ve a: https://shell.cloud.google.com

### 2. Configurar el proyecto
```bash
gcloud config set project gen-lang-client-0776831973
```

### 3. Clonar o actualizar el repositorio
```bash
# Si es primera vez:
git clone https://github.com/Proyecto-Docencia/backend.git
cd backend

# Si ya existe:
cd backend
git pull origin master
```

### 4. Verificar que los archivos esten correctos
```bash
# Verificar puerto BD
cat src/config/settings.py | grep DB_PORT
# Debe mostrar: 'PORT': os.environ.get('DB_PORT', '3306'),

# Listar archivos
ls -la
```

### 5. Desplegar con Cloud Build (RECOMENDADO - Mas rapido)
```bash
gcloud builds submit --config cloudbuild.yaml
```

**O desplegar manualmente:**

```bash
# A. Construir imagen
docker build -t gcr.io/gen-lang-client-0776831973/backend-django:latest .

# B. Subir imagen
docker push gcr.io/gen-lang-client-0776831973/backend-django:latest

# C. Desplegar a Cloud Run
gcloud run deploy backend-django \
  --image gcr.io/gen-lang-client-0776831973/backend-django:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 600s \
  --memory 2Gi \
  --cpu 1 \
  --add-cloudsql-instances gen-lang-client-0776831973:us-central1:admin123 \
  --set-env-vars "PORT=8080,DJANGO_SECRET_KEY=mi-secret-key-super-segura-para-produccion-2024,DJANGO_DEBUG=0,DJANGO_ALLOWED_HOSTS=*.run.app,.run.app,DB_ENGINE=mysql,DB_HOST=/cloudsql/gen-lang-client-0776831973:us-central1:admin123,DB_PORT=3306,DB_NAME=admin123,DB_USER=admin123,DB_PASSWORD=tuchangoGG123#,CORS_ALLOW_ALL_ORIGINS=1,CSRF_TRUSTED_ORIGINS=https://*.run.app,ENABLE_RAG=0"
```

### 6. Verificar despliegue
```bash
# Obtener URL del servicio
gcloud run services describe backend-django --region us-central1 --format='value(status.url)'

# Probar health check
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

**Respuesta esperada:**
```json
{"ok": true, "db_vendor": "mysql"}
```

### 7. Ver logs (si hay problemas)
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --format=json
```

---

## 📝 Cambios Importantes en esta Version

✅ **Puerto BD corregido**: 3306 (antes 3307)
✅ **Entrypoint mejorado**: Maneja errores, logs detallados
✅ **Variables de entorno**: PORT=8080, ALLOWED_HOSTS configurado
✅ **Scripts .sh**: Formato LF correcto para Linux
✅ **Documentacion**: 9 archivos markdown con guias completas

---

## 🔧 Si hay errores

### Error: Container failed to start
```bash
# Ver logs detallados
gcloud run services logs read backend-django --region us-central1 --limit 100
```

### Error: Database connection
```bash
# Verificar Cloud SQL
gcloud sql instances describe admin123
```

### Reconstruir desde cero
```bash
# Limpiar imagen anterior
gcloud container images delete gcr.io/gen-lang-client-0776831973/backend-django:latest --quiet

# Construir y desplegar nuevamente
gcloud builds submit --config cloudbuild.yaml
```

---

## 📊 URLs del Servicio

- **Health Check**: https://backend-django-79197934609.us-central1.run.app/healthz
- **API v1**: https://backend-django-79197934609.us-central1.run.app/api/v1/
- **Status**: https://backend-django-79197934609.us-central1.run.app/

---

## ✅ Checklist Post-Despliegue

- [ ] Health check responde: `{"ok": true, "db_vendor": "mysql"}`
- [ ] No hay errores en logs
- [ ] Frontend puede conectarse al backend
- [ ] Endpoints de API funcionan

---

**Fecha**: 17 de octubre, 2025
**Repositorio**: https://github.com/Proyecto-Docencia/backend
**Rama**: master
