from typing import Any, Dict
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.db import connection
from django.shortcuts import render


def healthz(_request: HttpRequest) -> JsonResponse:
    """Lightweight health endpoint.
    - Verifies DB connectivity by running a trivial SELECT 1
    - Returns JSON with status and minimal info
    """
    db_ok = False
    details = {}
    try:
        # Ensure connection and run a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_ok = True
        details["db_vendor"] = connection.vendor
    except Exception as exc:
        details["db_error"] = str(exc)

    status_code = 200 if db_ok else 503
    return JsonResponse({"ok": db_ok, **details}, status=status_code)


def hola(_request: HttpRequest) -> HttpResponse:
    """Renderiza una página simple 'Hola Mundo'."""
    return render(_request, 'hola.html')


def dbcheck(_request: HttpRequest) -> JsonResponse:
    """DB check with extra details.
    - Executes SELECT 1 and SELECT VERSION()
    - Returns vendor, version, and database name
    """
    payload: Dict[str, Any] = {"ok": False}
    try:
        with connection.cursor() as cursor:
            # Basic connectivity
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Server version
            cursor.execute("SELECT VERSION()")
            version_row = cursor.fetchone()
            server_version = version_row[0] if version_row else None

        payload["ok"] = True
        payload["db_vendor"] = connection.vendor
        payload["db_name"] = connection.settings_dict.get("NAME")
        payload["server_version"] = server_version
        status = 200
    except Exception as exc:
        payload["ok"] = False
        payload["db_error"] = str(exc)
        status = 503

    return JsonResponse(payload, status=status)
