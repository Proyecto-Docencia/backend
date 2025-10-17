# 🔧 Solución al Error de Cloud Run

## ❌ Error Original
```
Revision 'backend-django-00011-4jw' is not ready and cannot serve traffic.
The user-provided container failed to start and listen on the port defined 
provided by the PORT=8080 environment variable within the allocated timeout.
```

## 🔍 Problemas Identificados

### 1. **Puerto incorrecto en settings.py**
- **Problema**: `DB_PORT` estaba configurado en `3307` por defecto
- **Solución**: Cambiado a `3306` (puerto estándar de MySQL)

### 2. **Entrypoint muy estricto**
- **Problema**: El script `entrypoint.sh` fallaba completamente si la BD no estaba disponible
- **Solución**: Ahora permite arrancar el servidor incluso con problemas de BD para debugging

### 3. **Falta variable PORT explícita**
- **Problema**: Cloud Run requiere que el contenedor escuche en `$PORT` (8080)
- **Solución**: Agregada variable `PORT=8080` explícitamente en las env vars

### 4. **ALLOWED_HOSTS no configurado**
- **Problema**: Django rechazaba requests de dominios `.run.app`
- **Solución**: Agregada variable `DJANGO_ALLOWED_HOSTS=*.run.app,.run.app`

## ✅ Cambios Realizados

### 1. `backend/src/config/settings.py`
```python
# ANTES
'PORT': os.environ.get('DB_PORT', '3307'),

# DESPUÉS
'PORT': os.environ.get('DB_PORT', '3306'),
```

### 2. `backend/entrypoint.sh`
- ✅ Logs más informativos con el puerto que usa Gunicorn
- ✅ Opción `SKIP_DB_WAIT=1` para saltar espera de BD
- ✅ Continúa arranque incluso si BD falla (solo advierte)
- ✅ Workers reducidos a 2 (mejor para memoria)
- ✅ Timeout aumentado a 120s
- ✅ Logs de acceso y errores habilitados

### 3. `backend/backend/cloudbuild.yaml`
- ✅ Agregada variable `PORT=8080`
- ✅ Agregada variable `DJANGO_ALLOWED_HOSTS`
- ✅ Agregada variable `SKIP_DB_WAIT` (para debugging)

### 4. `backend/deploy-cloudrun.sh` (NUEVO)
- Script bash para despliegue directo sin Cloud Build
- Más rápido para pruebas y debugging

## 🚀 Cómo Desplegar Ahora

### Opción 1: Con Cloud Build (recomendado para producción)
```bash
cd backend
gcloud builds submit --config backend/cloudbuild.yaml
```

### Opción 2: Despliegue directo (más rápido para pruebas)
```bash
cd backend
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

### Opción 3: Despliegue manual paso a paso
```bash
cd backend

# 1. Construir imagen
docker build -t gcr.io/gen-lang-client-0776831973/backend-django:latest .

# 2. Subir a GCR
docker push gcr.io/gen-lang-client-0776831973/backend-django:latest

# 3. Desplegar
gcloud run deploy backend-django \
  --image gcr.io/gen-lang-client-0776831973/backend-django:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances gen-lang-client-0776831973:us-central1:admin123 \
  --set-env-vars "PORT=8080,DJANGO_ALLOWED_HOSTS=*.run.app,DB_HOST=/cloudsql/gen-lang-client-0776831973:us-central1:admin123,DB_PORT=3306,DB_NAME=admin123,DB_USER=admin123,DB_PASSWORD=tuchangoGG123#"
```

## 🔍 Debugging

### Si el contenedor sigue sin arrancar:

1. **Ver logs en tiempo real:**
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --format=json
```

2. **Revisar última revisión:**
```bash
gcloud run revisions list --service=backend-django --region=us-central1
```

3. **Probar localmente:**
```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e DB_HOST=localhost \
  -e DB_PORT=3306 \
  -e SKIP_DB_WAIT=1 \
  gcr.io/gen-lang-client-0776831973/backend-django:latest
```

### Si hay problemas de conexión a Cloud SQL:

1. **Verificar instancia de Cloud SQL:**
```bash
gcloud sql instances describe admin123
```

2. **Verificar usuario y permisos:**
```bash
gcloud sql users list --instance=admin123
```

3. **Probar conexión local con Cloud SQL Proxy:**
```bash
cloud_sql_proxy -instances=gen-lang-client-0776831973:us-central1:admin123=tcp:3306
mysql -h 127.0.0.1 -u admin123 -p admin123
```

## 📝 Variables de Entorno Críticas

Estas son las variables que DEBE tener configuradas Cloud Run:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `PORT` | `8080` | Puerto que Cloud Run espera |
| `DJANGO_ALLOWED_HOSTS` | `*.run.app,.run.app` | Hosts permitidos por Django |
| `DB_HOST` | `/cloudsql/PROJECT:REGION:INSTANCE` | Socket de Cloud SQL |
| `DB_PORT` | `3306` | Puerto MySQL |
| `DB_NAME` | `admin123` | Nombre de la base de datos |
| `DB_USER` | `admin123` | Usuario de la BD |
| `DB_PASSWORD` | `tuchangoGG123#` | Password de la BD |

## 🎯 Siguiente Paso

Despliega nuevamente con:
```bash
cd backend
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

O si prefieres usar Cloud Build:
```bash
gcloud builds submit --config backend/cloudbuild.yaml
```

Luego verifica que arranque:
```bash
curl https://backend-django-79197934609.us-central1.run.app/api/v1/health/
```
