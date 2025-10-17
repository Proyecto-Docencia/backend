# ✅ Checklist de Verificación - Cloud Run Deployment

## Antes de Desplegar

- [ ] **Proyecto de Google Cloud configurado**
  ```powershell
  gcloud config get-value project
  # Debe mostrar: gen-lang-client-0776831973
  ```

- [ ] **Docker corriendo**
  ```powershell
  docker --version
  docker ps
  ```

- [ ] **Autenticación con GCloud configurada**
  ```powershell
  gcloud auth list
  gcloud auth configure-docker gcr.io
  ```

- [ ] **Cloud SQL instancia activa**
  ```powershell
  gcloud sql instances describe admin123 --format="value(state)"
  # Debe mostrar: RUNNABLE
  ```

## Durante el Despliegue

- [ ] **Construcción de imagen exitosa**
  - No hay errores de build
  - Todas las dependencias se instalan correctamente

- [ ] **Push a GCR exitoso**
  - Imagen subida correctamente
  - Tag `latest` actualizado

- [ ] **Despliegue a Cloud Run exitoso**
  - Revisión creada sin errores
  - URL del servicio generada

## Después del Despliegue

### 1. Health Check Básico
- [ ] **Endpoint healthz responde**
  ```powershell
  curl https://backend-django-79197934609.us-central1.run.app/healthz
  ```
  **Respuesta esperada:**
  ```json
  {"ok": true, "db_vendor": "mysql"}
  ```

### 2. API Endpoints
- [ ] **Status HTML carga**
  ```powershell
  curl https://backend-django-79197934609.us-central1.run.app/
  ```

- [ ] **API v1 funciona**
  ```powershell
  curl https://backend-django-79197934609.us-central1.run.app/api/v1/auth/
  ```

### 3. Conexión a Base de Datos
- [ ] **Puede ejecutar migraciones**
  - Verificar en logs que no hay errores de migración
  
- [ ] **Puede leer/escribir en BD**
  - Crear un usuario de prueba
  - Verificar que se guarda correctamente

### 4. Logs y Monitoreo
- [ ] **Logs no muestran errores críticos**
  ```powershell
  gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --limit 50
  ```

- [ ] **Métricas de Cloud Run normales**
  - CPU < 80%
  - Memoria < 1.5Gi
  - Latencia < 2s
  - No hay errores 5xx

### 5. CORS y Seguridad
- [ ] **CORS configurado correctamente**
  - Frontend puede hacer requests al backend
  
- [ ] **CSRF funciona**
  - Tokens se generan correctamente
  
- [ ] **ALLOWED_HOSTS configurado**
  - No hay errores de "DisallowedHost"

## Troubleshooting

### Si el contenedor no arranca:
1. [ ] Ver logs completos:
   ```powershell
   gcloud run services logs read backend-django --region us-central1 --limit 100
   ```

2. [ ] Verificar variables de entorno:
   ```powershell
   gcloud run services describe backend-django --region us-central1 --format="value(spec.template.spec.containers[0].env)"
   ```

3. [ ] Verificar conexión Cloud SQL:
   ```powershell
   gcloud sql connect admin123 --user=admin123
   ```

### Si hay errores de BD:
1. [ ] Verificar que la instancia Cloud SQL está conectada:
   ```powershell
   gcloud run services describe backend-django --region us-central1 --format="value(spec.template.metadata.annotations.run.googleapis.com/cloudsql-instances)"
   ```

2. [ ] Verificar credenciales:
   - Usuario: `admin123`
   - Base de datos: `admin123`
   - Host: `/cloudsql/gen-lang-client-0776831973:us-central1:admin123`

### Si hay errores 500:
1. [ ] Activar DEBUG temporalmente:
   ```powershell
   gcloud run services update backend-django --region us-central1 --update-env-vars DJANGO_DEBUG=1
   ```

2. [ ] Ver traceback completo en logs

3. [ ] Desactivar DEBUG después:
   ```powershell
   gcloud run services update backend-django --region us-central1 --update-env-vars DJANGO_DEBUG=0
   ```

## Variables de Entorno Críticas

Verificar que estas variables estén configuradas:

- [ ] `PORT=8080`
- [ ] `DJANGO_SECRET_KEY` (no vacío)
- [ ] `DJANGO_ALLOWED_HOSTS=*.run.app,.run.app`
- [ ] `DB_HOST=/cloudsql/gen-lang-client-0776831973:us-central1:admin123`
- [ ] `DB_PORT=3306`
- [ ] `DB_NAME=admin123`
- [ ] `DB_USER=admin123`
- [ ] `DB_PASSWORD` (configurado correctamente)
- [ ] `CORS_ALLOW_ALL_ORIGINS=1` o `CORS_ALLOWED_ORIGINS` configurado

## Comandos Útiles

```powershell
# Ver última revisión
gcloud run revisions list --service backend-django --region us-central1 --limit 1

# Eliminar revisiones antiguas
gcloud run revisions delete REVISION_NAME --region us-central1

# Actualizar una variable de entorno
gcloud run services update backend-django --region us-central1 --update-env-vars KEY=VALUE

# Escalar instancias
gcloud run services update backend-django --region us-central1 --min-instances 1 --max-instances 10

# Ver estado del servicio
gcloud run services describe backend-django --region us-central1
```

## Resultados Esperados

✅ **TODO OK cuando:**
- Health check responde 200 con `{"ok": true}`
- Logs muestran: `[entrypoint] Lanzando gunicorn en 0.0.0.0:8080`
- No hay errores de conexión a BD
- Frontend puede conectarse al backend
- Requests responden en < 2 segundos

---

**Última actualización**: 2025-10-17
**Versión del checklist**: 1.0
