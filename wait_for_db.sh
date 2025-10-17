#!/bin/sh
set -e

HOST="${DB_HOST:-localhost}"
PORT="${DB_PORT:-3306}"
ENGINE="${DB_ENGINE:-mysql}"
USER="${DB_USER}"
PASS="${DB_PASSWORD:-${DB_PASS}}"
NAME="${DB_NAME}"
MAX_RETRIES=${DB_WAIT_RETRIES:-30}
SLEEP_SECONDS=${DB_WAIT_INTERVAL:-2}

echo "[wait_for_db] Esperando base de datos $ENGINE en $HOST:$PORT (db=$NAME user=$USER)"

if [ "${DB_DEBUG}" = "1" ]; then
    pw="${PASS}"
    pw_len=${#pw}
    # Obtener primer y Ãºltimo carÃ¡cter de forma POSIX (sin expansiones bash)
    if [ "$pw_len" -gt 0 ]; then
        first_char=`printf '%s' "$pw" | cut -c1`
        last_char=`printf '%s' "$pw" | rev | cut -c1`
    else
        first_char=""; last_char=""
    fi
    printf '[wait_for_db][debug] Password len=%s first_char=%s last_char=%s\n' "$pw_len" "$first_char" "$last_char"
    case "$first_char" in '"') echo '[wait_for_db][debug] ADVERTENCIA: primer caracter es comilla (revisa .env)';; esac
    case "$last_char" in '"') echo '[wait_for_db][debug] ADVERTENCIA: Ãºltimo caracter es comilla (revisa .env)';; esac
fi

python <<PY
import os, sys, time, traceback

HOST = os.environ.get('DB_HOST', 'localhost')
PORT = int(os.environ.get('DB_PORT', '3306'))
ENGINE = os.environ.get('DB_ENGINE', 'mysql').lower()
USER = os.environ.get('DB_USER')
PASS = os.environ.get('DB_PASSWORD') or os.environ.get('DB_PASS')
NAME = os.environ.get('DB_NAME')
MAX_RETRIES = int(os.environ.get('DB_WAIT_RETRIES', '30'))
SLEEP = int(os.environ.get('DB_WAIT_INTERVAL', '2'))

def log(msg):
    print(f"[wait_for_db] {msg}", flush=True)

for attempt in range(1, MAX_RETRIES+1):
    try:
        if ENGINE.startswith('postg'):
            import psycopg
            psycopg.connect(host=HOST, port=PORT, user=USER, password=PASS, dbname=NAME, connect_timeout=3).close()
            log('ConexiÃ³n PostgreSQL OK')
            break
        else:
            import MySQLdb
            # Si HOST apunta a un socket Unix de Cloud SQL (p. ej., /cloudsql/PROJECT:REGION:INSTANCE)
            if isinstance(HOST, str) and HOST.startswith('/cloudsql/'):
                MySQLdb.connect(unix_socket=HOST, user=USER, passwd=PASS, db=NAME, connect_timeout=3).close()
            else:
                MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASS, db=NAME, connect_timeout=3).close()
            log('ConexiÃ³n MySQL OK')
            break
    except Exception as e:
        # Manejo especÃ­fico para error 1045 (Access denied)
        if '1045' in str(e):
            log(f"ERROR acceso denegado (1045) en intento {attempt}: {e}")
            log("GuÃ­a rÃ¡pida: 1) Verifica usuario y password. 2) Comprueba con mysql CLI: mysql -h 127.0.0.1 -P $PORT -u $USER -p 3) Crea usuario / otorga privilegios si falta. 4) Asegura que la DB existe: SHOW DATABASES LIKE '%s';" % NAME)
            traceback.print_exc()
            sys.exit(2)
        log(f"Intento {attempt}/{MAX_RETRIES} fallÃ³: {e}")
        traceback.print_exc()
        if attempt == MAX_RETRIES:
            log('ERROR: No se pudo conectar a la base de datos. Abortando.')
            sys.exit(1)
        time.sleep(SLEEP)
else:
    sys.exit(1)

log('Listo. Continuando.')
PY
