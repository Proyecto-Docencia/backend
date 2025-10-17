import os
from pathlib import Path
from typing import Any, Dict

# Cargar variables desde env/.env si existe
try:
    from dotenv import load_dotenv  # type: ignore
    # Intentar primero ruta montada en contenedor /app/env/.env
    candidate_paths = [
        Path('/app/env/.env'),
        Path(__file__).resolve().parent.parent.parent / 'env' / '.env'
    ]
    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except Exception:
    # Silencioso: si no existe python-dotenv o el archivo, continuar con variables del entorno
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Hosts permitidos (coma separada). Ej: "miapp.azurewebsites.net,api.midominio.com"
_raw_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "*")
ALLOWED_HOSTS: list[str] = [h.strip() for h in _raw_hosts.split(',')] if _raw_hosts else ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'auth_app',
    'plans_app',
    'chat_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES: list[dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

_db_password = os.environ.get('DB_PASSWORD') or os.environ.get('DB_PASS') or 'rootpass'

# Construir configuración de DB en una variable temporal tipada y luego asignar a DATABASES.
_db_config: Dict[str, Any]
if os.environ.get('DJANGO_TEST') == '1':
    # Entorno de test: usar SQLite en memoria
    _db_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
else:
    _db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'proyecto'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': _db_password,
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4'
        }
    }
    # Ajuste automático para Cloud SQL por Unix Socket en Cloud Run.
    _db_host_val = str(_db_config.get('HOST') or '')
    if _db_host_val.startswith('/cloudsql/'):
        # mysqlclient con Cloud SQL por socket
        _db_config['HOST'] = ''
        _db_config.setdefault('OPTIONS', {})['unix_socket'] = _db_host_val

DATABASES: Dict[str, Dict[str, Any]] = {
    'default': _db_config
}

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth_app.CustomUser'

# CORS dinámico (coma separada). Ej: "https://www.midominio.com,https://app.midominio.com"
_raw_cors = os.environ.get("CORS_ALLOWED_ORIGINS")
_allow_all_flag = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "0").lower() in {"1", "true", "yes"}

# Calcular configuración CORS/CSRF usando variables locales primero
_cors_allow_all_final: bool
_cors_allowed_list_final: list[str]

if _allow_all_flag:
    _cors_allow_all_final = True
    _cors_allowed_list_final = []
elif _raw_cors:
    tokens = [o.strip() for o in _raw_cors.split(',') if o.strip()]
    if '*' in tokens or _raw_cors.strip() == '*':
        _cors_allow_all_final = True
        _cors_allowed_list_final = []
    else:
        _cors_allow_all_final = False
        _cors_allowed_list_final = tokens
else:
    _cors_allow_all_final = False
    _cors_allowed_list_final = ['http://localhost:8080']

# CSRF trusted origins (usar mismo formato que CORS). Debe incluir schema.
_raw_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS")
if _raw_csrf:
    _csrf_trusted_list: list[str] = [o.strip() for o in _raw_csrf.split(',') if o.strip()]
else:
    # Por defecto reflejamos CORS si están en http/https
    _csrf_trusted_list = [
        o for o in _cors_allowed_list_final
        if o.startswith('http://') or o.startswith('https://')
    ]

# Asignar constantes una sola vez para evitar redefiniciones
CORS_ALLOW_ALL_ORIGINS: bool = _cors_allow_all_final
CORS_ALLOWED_ORIGINS: list[str] = [] if _cors_allow_all_final else _cors_allowed_list_final
CSRF_TRUSTED_ORIGINS: list[str] = _csrf_trusted_list

CORS_ALLOW_CREDENTIALS = True
