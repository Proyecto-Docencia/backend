from django.contrib import admin
from django.urls import path, include
from .views import healthz, hola, dbcheck

# --- Versionamiento: nueva raíz /api/v1/ ---
# Mantiene compatibilidad con rutas existentes
api_v1_patterns = [
    path('auth/', include('auth_app.urls')),
    path('plans/', include('plans_app.urls')),
    path('chat/', include('chat_app.urls')),
    path('rag/', include('rag_proxy.urls')),
]

 urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # --- Variantes de health para compatibilidad con GFE/monitores ---
    path('healthz', healthz, name='healthz'),
    path('healthz/', healthz, name='healthz-slash'),
    path('health', healthz, name='health'),
    path('health/', healthz, name='health-slash'),
    path('_healthz', healthz, name='_healthz'),
    path('_healthz/', healthz, name='_healthz-slash'),

    # --- DB checks ---
    path('dbcheck', dbcheck, name='dbcheck'),
    path('dbcheck/', dbcheck, name='dbcheck-slash'),
    path('_dbcheck', dbcheck, name='_dbcheck'),
    path('_dbcheck/', dbcheck, name='_dbcheck-slash'),

    # --- Endpoints básicos ---
    path('hola', hola, name='hola'),
    path('', hola, name='root'),

    # --- Nuevas rutas versionadas ---
    path('api/v1/', include((api_v1_patterns, 'api_v1'))),

    # --- Alias legacy (transición) ---
    # Eliminar cuando el frontend migre completamente
    path('api/auth/', include('auth_app.urls')),
    path('api/plans/', include('plans_app.urls')),
    path('api/chat/', include('chat_app.urls')),
    path('api/rag/', include('rag_proxy.urls')),
]
