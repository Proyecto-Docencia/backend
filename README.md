# 🚀 Backend Django - Cloud Run Deployment

Backend Django para sistema de planificación educativa con IA, desplegado en Google Cloud Run con Cloud SQL.

## 📋 Contenido

- [Inicio Rápido](#inicio-rápido)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)
- [Despliegue](#despliegue)
- [Variables de Entorno](#variables-de-entorno)
- [Desarrollo Local](#desarrollo-local)

---

## 🚀 Inicio Rápido

### Despliegue a Cloud Run (Producción)

**Windows PowerShell:**
```powershell
.\deploy-cloudrun.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

### Verificar Despliegue
```bash
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

---

## 📁 Estructura del Proyecto

```
backend/
├── 📄 README.md                    # Este archivo
├── 📄 Dockerfile                   # Configuración Docker para Cloud Run
├── 📄 entrypoint.sh               # Script de inicio del contenedor
├── 📄 wait_for_db.sh              # Script de espera de base de datos
├── 📄 requirements.txt            # Dependencias principales
├── 📄 requirements-rag.txt        # Dependencias RAG (opcional)
│
├── 🚀 DESPLIEGUE
│   ├── cloudbuild.yaml            # Configuración Cloud Build
│   ├── deploy-cloudrun.ps1        # Script despliegue Windows
│   ├── deploy-cloudrun.sh         # Script despliegue Linux/Mac
│   ├── .gcloudignore              # Archivos a ignorar en GCloud
│   └── deploy.sh                  # Script legacy
│
├── 📚 DOCUMENTACIÓN
│   ├── RESUMEN_SOLUCION.md        # ⭐ Resumen ejecutivo de cambios
│   ├── SOLUCION_CLOUD_RUN.md      # 🔧 Guía técnica completa
│   ├── CHECKLIST_DEPLOYMENT.md    # ✅ Checklist de verificación
│   ├── README_LOCAL_DEV.md        # 💻 Desarrollo local
│   └── README_RAG.md              # 🤖 RAG (Retrieval-Augmented Generation)
│
├── ⚙️ CONFIGURACIÓN
│   ├── .env.example               # Ejemplo variables de entorno
│   └── env.example                # Alias del anterior
│
└── 📦 src/                        # Código fuente Django
    ├── manage.py
    ├── config/                    # Configuración Django
    │   ├── settings.py           # ✏️ Configuración principal
    │   ├── urls.py               # Rutas API
    │   └── views.py              # Vistas (health checks)
    ├── auth_app/                  # Autenticación
    ├── chat_app/                  # Chat con IA
    ├── plans_app/                 # Planificaciones
    └── rag_proxy/                 # RAG opcional
```

---

## 📚 Documentación

### Documentos Clave (en orden de lectura):

1. **[RESUMEN_SOLUCION.md](./RESUMEN_SOLUCION.md)** 
   - ⭐ **LEE ESTO PRIMERO**
   - Resumen ejecutivo de los cambios realizados
   - Qué problemas se solucionaron
   - Cómo desplegar ahora

2. **[SOLUCION_CLOUD_RUN.md](./SOLUCION_CLOUD_RUN.md)**
   - 🔧 Guía técnica completa
   - Explicación detallada de cada cambio
   - Comandos de debugging
   - Troubleshooting

3. **[CHECKLIST_DEPLOYMENT.md](./CHECKLIST_DEPLOYMENT.md)**
   - ✅ Checklist paso a paso
   - Verificaciones pre/post despliegue
   - Comandos útiles

4. **[README_LOCAL_DEV.md](./README_LOCAL_DEV.md)**
   - 💻 Desarrollo local con Docker
   - Configuración de base de datos local
   - Hot-reload y debugging

5. **[README_RAG.md](./README_RAG.md)**
   - 🤖 Sistema RAG (opcional)
   - Retrieval-Augmented Generation
   - Configuración de vectores

---

## 🚀 Despliegue

### Opción 1: Script Automatizado (Recomendado)

**Windows:**
```powershell
cd backend
.\deploy-cloudrun.ps1
```

**Linux/Mac:**
```bash
cd backend
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

### Opción 2: Cloud Build
```bash
gcloud builds submit --config cloudbuild.yaml
```

### Opción 3: Manual
```bash
# 1. Construir
docker build -t gcr.io/gen-lang-client-0776831973/backend-django:latest .

# 2. Subir
docker push gcr.io/gen-lang-client-0776831973/backend-django:latest

# 3. Desplegar
gcloud run deploy backend-django \
  --image gcr.io/gen-lang-client-0776831973/backend-django:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances gen-lang-client-0776831973:us-central1:admin123 \
  --set-env-vars "PORT=8080,DJANGO_ALLOWED_HOSTS=*.run.app,DB_HOST=/cloudsql/gen-lang-client-0776831973:us-central1:admin123"
```

---

## 🔧 Variables de Entorno

### Variables Críticas (Cloud Run)

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `PORT` | `8080` | Puerto para Cloud Run |
| `DJANGO_SECRET_KEY` | `[secret]` | Clave secreta Django |
| `DJANGO_ALLOWED_HOSTS` | `*.run.app,.run.app` | Hosts permitidos |
| `DB_ENGINE` | `mysql` | Motor de base de datos |
| `DB_HOST` | `/cloudsql/[INSTANCE]` | Socket Cloud SQL |
| `DB_PORT` | `3306` | Puerto MySQL |
| `DB_NAME` | `admin123` | Nombre de la BD |
| `DB_USER` | `admin123` | Usuario BD |
| `DB_PASSWORD` | `[secret]` | Password BD |
| `CORS_ALLOW_ALL_ORIGINS` | `1` | Permitir todos los orígenes CORS |
| `CSRF_TRUSTED_ORIGINS` | `https://*.run.app` | Orígenes confiables |

### Variables Opcionales

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DJANGO_DEBUG` | `0` | Modo debug (0=off, 1=on) |
| `ENABLE_RAG` | `0` | Habilitar RAG |
| `SKIP_DB_WAIT` | `0` | Saltar espera de BD (debug) |
| `GUNICORN_WORKERS` | `2` | Workers de Gunicorn |
| `GUNICORN_TIMEOUT` | `120` | Timeout Gunicorn (segundos) |

---

## 💻 Desarrollo Local

### Con Docker Compose
```bash
# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus valores locales
# DB_HOST=db, DB_PORT=3306, etc.

# Levantar servicios
docker-compose up --build
```

### Sin Docker
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con valores locales

# Migrar BD
python src/manage.py migrate

# Ejecutar servidor
python src/manage.py runserver 0.0.0.0:8000
```

Ver: **[README_LOCAL_DEV.md](./README_LOCAL_DEV.md)** para más detalles.

---

## 🔍 Health Checks

### Endpoints Disponibles

- **`/healthz`** - Health check básico con verificación de BD
  ```bash
  curl https://backend-django-79197934609.us-central1.run.app/healthz
  # Respuesta: {"ok": true, "db_vendor": "mysql"}
  ```

- **`/`** - Status HTML
  ```bash
  curl https://backend-django-79197934609.us-central1.run.app/
  ```

- **`/api/v1/`** - API endpoints versionados
  - `/api/v1/auth/` - Autenticación
  - `/api/v1/plans/` - Planificaciones
  - `/api/v1/chat/` - Chat IA
  - `/api/v1/rag/` - RAG (si está habilitado)

---

## 🐛 Troubleshooting

### Ver Logs
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --format=json
```

### Ver Última Revisión
```bash
gcloud run revisions list --service=backend-django --region=us-central1
```

### Probar Localmente
```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e SKIP_DB_WAIT=1 \
  gcr.io/gen-lang-client-0776831973/backend-django:latest
```

### Problemas Comunes

1. **Container failed to start**
   - Ver: [SOLUCION_CLOUD_RUN.md](./SOLUCION_CLOUD_RUN.md)
   - Verificar variables de entorno
   - Revisar logs

2. **Error de conexión a BD**
   - Verificar Cloud SQL instance
   - Verificar credenciales
   - Verificar socket path

3. **Error 500**
   - Activar DEBUG temporalmente
   - Ver traceback en logs
   - Verificar ALLOWED_HOSTS

Ver: **[CHECKLIST_DEPLOYMENT.md](./CHECKLIST_DEPLOYMENT.md)** para más soluciones.

---

## 📊 Stack Tecnológico

- **Framework**: Django 4.2+
- **WSGI Server**: Gunicorn
- **Base de Datos**: MySQL (Cloud SQL)
- **Cloud**: Google Cloud Run
- **Container**: Docker
- **IA**: Google Generative AI
- **RAG**: (Opcional) Vector embeddings

---

## 🔗 URLs Importantes

- **Producción**: https://backend-django-79197934609.us-central1.run.app
- **Health Check**: https://backend-django-79197934609.us-central1.run.app/healthz
- **API v1**: https://backend-django-79197934609.us-central1.run.app/api/v1/
- **Cloud Console**: https://console.cloud.google.com/run?project=gen-lang-client-0776831973

---

## 📝 Cambios Recientes (Oct 2025)

✅ **Problemas Solucionados:**
- Puerto de BD corregido (3307 → 3306)
- Entrypoint mejorado (permite arranque con BD no disponible)
- Variables de entorno agregadas (PORT, ALLOWED_HOSTS)
- Scripts de despliegue creados (PowerShell y Bash)
- Documentación completa actualizada

Ver: **[RESUMEN_SOLUCION.md](./RESUMEN_SOLUCION.md)** para detalles completos.

---

## 👥 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es privado - Proyecto Docencia USS

---

## 🆘 Soporte

¿Problemas? Revisa la documentación en este orden:

1. 📄 [RESUMEN_SOLUCION.md](./RESUMEN_SOLUCION.md) - Inicio rápido
2. 🔧 [SOLUCION_CLOUD_RUN.md](./SOLUCION_CLOUD_RUN.md) - Guía técnica
3. ✅ [CHECKLIST_DEPLOYMENT.md](./CHECKLIST_DEPLOYMENT.md) - Verificación
4. 💻 [README_LOCAL_DEV.md](./README_LOCAL_DEV.md) - Desarrollo local

---

**Última actualización**: 17 de octubre, 2025  
**Versión**: 2.0 - Cloud Run Optimizado
