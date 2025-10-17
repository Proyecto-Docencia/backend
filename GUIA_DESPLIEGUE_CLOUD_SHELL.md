# Guia para Subir Cambios y Desplegar desde Google Cloud Shell

## PARTE 1: SUBIR CAMBIOS AL REPOSITORIO (Desde tu PC)

### 1. Verificar el estado actual
```powershell
cd "c:\dev\ia docencia\GITHUB\version rial\Proyecto-main\Proyecto-main"
git status
```

### 2. Agregar todos los cambios
```powershell
git add backend/
```

### 3. Hacer commit con mensaje descriptivo
```powershell
git commit -m "Fix: Backend optimizado para Cloud Run - Puerto BD corregido, scripts mejorados, documentacion completa"
```

### 4. Verificar repositorio remoto
```powershell
git remote -v
```

### 5. Subir cambios a GitHub
```powershell
git push origin main
```

Si te pide autenticacion, usa tu token de GitHub o credenciales.

---

## PARTE 2: DESPLEGAR DESDE GOOGLE CLOUD SHELL

### 1. Abrir Google Cloud Shell
- Ve a: https://console.cloud.google.com
- Click en el icono de terminal (arriba a la derecha)
- O ve directo a: https://shell.cloud.google.com

### 2. Verificar proyecto activo
```bash
gcloud config get-value project
# Debe mostrar: gen-lang-client-0776831973
```

Si no es el correcto:
```bash
gcloud config set project gen-lang-client-0776831973
```

### 3. Clonar o actualizar el repositorio
```bash
# Si es la primera vez:
git clone https://github.com/Proyecto-Docencia/Proyecto-main.git
cd Proyecto-main/backend

# Si ya existe el repo:
cd Proyecto-main
git pull origin main
cd backend
```

### 4. Verificar que los archivos esten bien
```bash
ls -la
cat src/config/settings.py | grep DB_PORT
# Debe mostrar: 'PORT': os.environ.get('DB_PORT', '3306'),
```

### 5. Construir y subir imagen a Container Registry
```bash
# Autenticar con Docker
gcloud auth configure-docker gcr.io

# Construir imagen
docker build -t gcr.io/gen-lang-client-0776831973/backend-django:latest .

# Subir imagen
docker push gcr.io/gen-lang-client-0776831973/backend-django:latest
```

### 6. Desplegar a Cloud Run
```bash
gcloud run deploy backend-django \
  --image gcr.io/gen-lang-client-0776831973/backend-django:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 600s \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --add-cloudsql-instances gen-lang-client-0776831973:us-central1:admin123 \
  --set-env-vars "\
PORT=8080,\
DJANGO_SECRET_KEY=mi-secret-key-super-segura-para-produccion-2024,\
DJANGO_DEBUG=0,\
DJANGO_ALLOWED_HOSTS=*.run.app,.run.app,\
DB_ENGINE=mysql,\
DB_HOST=/cloudsql/gen-lang-client-0776831973:us-central1:admin123,\
DB_PORT=3306,\
DB_NAME=admin123,\
DB_USER=admin123,\
DB_PASSWORD=tuchangoGG123#,\
CORS_ALLOW_ALL_ORIGINS=1,\
CSRF_TRUSTED_ORIGINS=https://*.run.app,\
ENABLE_RAG=0"
```

### 7. Verificar despliegue
```bash
# Obtener URL
gcloud run services describe backend-django --region us-central1 --format='value(status.url)'

# Probar health check
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

### 8. Ver logs (si hay problemas)
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --format=json
```

---

## OPCION ALTERNATIVA: Usar Cloud Build (Mas Rapido)

Si prefieres usar Cloud Build (mas automatizado):

### 1. Ir a la carpeta backend en Cloud Shell
```bash
cd Proyecto-main/backend
```

### 2. Usar el archivo cloudbuild.yaml
```bash
gcloud builds submit --config cloudbuild.yaml
```

Esto automaticamente:
- Construye la imagen
- La sube a Artifact Registry
- La despliega a Cloud Run

---

## VERIFICACION FINAL

### 1. Probar el endpoint de health
```bash
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

Respuesta esperada:
```json
{"ok": true, "db_vendor": "mysql"}
```

### 2. Probar el API
```bash
curl https://backend-django-79197934609.us-central1.run.app/api/v1/
```

### 3. Ver estado del servicio
```bash
gcloud run services list --region us-central1
```

---

## RESUMEN DE COMANDOS RAPIDOS

### Desde tu PC (Windows):
```powershell
# 1. Ir a la carpeta del proyecto
cd "c:\dev\ia docencia\GITHUB\version rial\Proyecto-main\Proyecto-main"

# 2. Subir cambios
git add backend/
git commit -m "Fix: Backend optimizado para Cloud Run"
git push origin main
```

### Desde Google Cloud Shell:
```bash
# 1. Configurar proyecto
gcloud config set project gen-lang-client-0776831973

# 2. Clonar/actualizar repo
git clone https://github.com/Proyecto-Docencia/Proyecto-main.git
# o: cd Proyecto-main && git pull origin main

# 3. Ir a backend y desplegar
cd Proyecto-main/backend
gcloud builds submit --config cloudbuild.yaml

# 4. Verificar
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

---

## PROBLEMAS COMUNES

### 1. Error de autenticacion en git push
```powershell
# Usar token de GitHub en vez de password
# O configurar SSH keys
```

### 2. Error "Permission denied" en Cloud Shell
```bash
# Verificar permisos
gcloud projects get-iam-policy gen-lang-client-0776831973

# O autenticarse de nuevo
gcloud auth login
```

### 3. Error en Cloud Build
```bash
# Ver logs detallados
gcloud builds log [BUILD_ID]

# O ver en la consola
# https://console.cloud.google.com/cloud-build/builds
```

---

## SIGUIENTE PASO INMEDIATO

Ejecuta estos comandos en orden:

**En tu PC (PowerShell):**
```powershell
cd "c:\dev\ia docencia\GITHUB\version rial\Proyecto-main\Proyecto-main"
git status
git add backend/
git commit -m "Fix: Backend optimizado para Cloud Run"
git push origin main
```

**Luego en Google Cloud Shell:**
1. Abre: https://shell.cloud.google.com
2. Ejecuta los comandos de la seccion "Desde Google Cloud Shell"

---

**Fecha**: 17 de octubre, 2025
**Ultima actualizacion**: Optimizado para Cloud Run v2.0
