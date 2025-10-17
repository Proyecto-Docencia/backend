# ⚡ INICIO RÁPIDO - Backend Django

## 🎯 Desplegar en 3 Pasos

### 1️⃣ Ir a la carpeta backend
```powershell
cd backend
```

### 2️⃣ Ejecutar script de despliegue
```powershell
.\deploy-cloudrun.ps1
```

### 3️⃣ Verificar que funcione
```powershell
curl https://backend-django-79197934609.us-central1.run.app/healthz
```

**Respuesta esperada:**
```json
{"ok": true, "db_vendor": "mysql"}
```

---

## 📚 Documentación

| Archivo | Propósito | ¿Cuándo leer? |
|---------|-----------|---------------|
| **[README.md](./README.md)** | 📘 Guía principal completa | Siempre primero |
| **[ESTRUCTURA_ORGANIZADA.md](./ESTRUCTURA_ORGANIZADA.md)** | 📁 Estructura de archivos | Para entender la organización |
| **[RESUMEN_SOLUCION.md](./RESUMEN_SOLUCION.md)** | ⭐ Qué se cambió y por qué | Para entender los cambios |
| **[SOLUCION_CLOUD_RUN.md](./SOLUCION_CLOUD_RUN.md)** | 🔧 Guía técnica detallada | Si tienes problemas |
| **[CHECKLIST_DEPLOYMENT.md](./CHECKLIST_DEPLOYMENT.md)** | ✅ Lista verificación | Antes/después de desplegar |
| **[README_LOCAL_DEV.md](./README_LOCAL_DEV.md)** | 💻 Desarrollo local | Para desarrollo |
| **[README_RAG.md](./README_RAG.md)** | 🤖 Sistema RAG | Si usas RAG |

---

## 🔍 Comandos Útiles

### Ver Logs
```powershell
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=backend-django" --format=json
```

### Ver Estado del Servicio
```powershell
gcloud run services describe backend-django --region us-central1
```

### Ver Última Revisión
```powershell
gcloud run revisions list --service=backend-django --region=us-central1 --limit 1
```

### Actualizar Variable de Entorno
```powershell
gcloud run services update backend-django --region us-central1 --update-env-vars KEY=VALUE
```

---

## 🆘 Problemas Comunes

### Container failed to start
➡️ Ver: [SOLUCION_CLOUD_RUN.md](./SOLUCION_CLOUD_RUN.md)

### Error de BD
```powershell
gcloud sql instances describe admin123
```

### Error 500
```powershell
# Activar DEBUG temporalmente
gcloud run services update backend-django --region us-central1 --update-env-vars DJANGO_DEBUG=1

# Ver logs
gcloud logging tail "resource.labels.service_name=backend-django" --format=json

# DESACTIVAR DEBUG después
gcloud run services update backend-django --region us-central1 --update-env-vars DJANGO_DEBUG=0
```

---

## 🌐 URLs Importantes

- **API**: https://backend-django-79197934609.us-central1.run.app
- **Health**: https://backend-django-79197934609.us-central1.run.app/healthz
- **Status**: https://backend-django-79197934609.us-central1.run.app/
- **API v1**: https://backend-django-79197934609.us-central1.run.app/api/v1/

---

## ✅ Estado Actual

- ✅ Código organizado en carpeta `backend/`
- ✅ Sin duplicados
- ✅ Puerto BD corregido (3306)
- ✅ Entrypoint mejorado
- ✅ Variables de entorno configuradas
- ✅ Scripts de despliegue listos
- ✅ Documentación completa

**🟢 LISTO PARA DESPLEGAR**

---

**Última actualización**: 17 de octubre, 2025
