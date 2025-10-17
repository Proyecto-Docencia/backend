#!/bin/sh
set -e

echo "[entrypoint] Arrancando backend"

# Normalizar DB_ENGINE si viene como 'postgresql'
if [ "$DB_ENGINE" = "postgresql" ]; then
	export DB_ENGINE=postgresql
fi

WAIT_STATUS=0
if [ -f /app/wait_for_db.sh ]; then
	chmod +x /app/wait_for_db.sh
	# Desactivar salida inmediata para capturar cÃ³digo especÃ­fico (2 = acceso denegado 1045)
	set +e
	/app/wait_for_db.sh
	WAIT_STATUS=$?
	set -e
else
	echo "[entrypoint] Script wait_for_db.sh no encontrado, continuando sin espera activa"
fi

if [ "$WAIT_STATUS" = "2" ]; then
	echo "[entrypoint] ERROR 1045 (Access denied) al conectar a la DB con el usuario '${DB_USER}'." >&2
	echo "[entrypoint] Sugerencias: revisar usuario/clave, privilegios y que la DB '${DB_NAME}' exista." >&2
	# En Cloud Run no podemos quedarnos bloqueados (no abrirÃ­amos el puerto). Detectar entorno por K_SERVICE.
	if [ -n "$K_SERVICE" ]; then
		echo "[entrypoint] EjecutÃ¡ndose en Cloud Run: saliendo con error para reinicio automÃ¡tico." >&2
		exit 1
	else
		echo "[entrypoint] Entorno local: dejando contenedor vivo para depuraciÃ³n (tail -f)."
		tail -f /dev/null
	fi
fi

if [ "$WAIT_STATUS" != "0" ]; then
	echo "[entrypoint] FallÃ³ la espera de la base de datos (cÃ³digo $WAIT_STATUS). Saliendo." >&2
	exit 1
fi

echo "[entrypoint] Ejecutando migraciones"
echo "[entrypoint] DB_ENGINE=$DB_ENGINE DB_HOST=$DB_HOST DB_PORT=$DB_PORT DB_NAME=$DB_NAME DB_USER=$DB_USER"
python manage.py migrate --noinput || {
	echo "[entrypoint] Migraciones fallaron" >&2
	exit 1
}

echo "[entrypoint] Lanzando gunicorn"
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers ${GUNICORN_WORKERS:-3}
