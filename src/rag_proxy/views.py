import json
import os
import time
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .retrieval import search, format_context
from chat_app.ai_service import consultar_gemini

# Desactivado por defecto hasta que el operador lo habilite explícitamente
ENABLE_RAG = os.environ.get("ENABLE_RAG", "0") == "1"


@csrf_exempt
@require_http_methods(["POST"])
def query_rag(request: HttpRequest):
    if not ENABLE_RAG:
        return JsonResponse({"error": "RAG desactivado", "enabled": False}, status=503)

    t0 = time.time()
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    mensaje = (payload.get("mensaje_usuario") or payload.get("question") or "").strip()
    if not mensaje:
        return JsonResponse({"error": "mensaje_usuario requerido"}, status=400)

    top_k = payload.get("top_k") or None
    # Retrieval
    results = search(mensaje, top_k=top_k)
    contexto = format_context(results) if results else ""

    # Construcción de prompt para Gemini reutilizando la función existente.
    if contexto:
        prompt = (
            "Eres un asistente pedagógico. Usa SOLO el contexto si responde a la pregunta. "
            "Si no está en el contexto di que no lo encuentras.\n\n"
            f"Contexto:\n{contexto}\nPregunta: {mensaje}\n\nRespuesta concisa (<=180 palabras) con fuentes al final:"  # noqa: E501
        )
    else:
        prompt = (
            "No se encontraron fragmentos relevantes. Responde de forma general sin inventar "
            "datos específicos de documentos. Pregunta: " + mensaje
        )

    respuesta = consultar_gemini(prompt)

    fuentes = [
        {
            "doc": r["doc"],
            "page": r["page"],
            "score": round(r["score"], 4),
            "preview": (r["text"][:160] + "…") if len(r["text"]) > 160 else r["text"],
        }
        for r in results
    ]

    return JsonResponse(
        {
            "respuesta_ia": respuesta,
            "fuentes": fuentes,
            "fallback_sin_contexto": not bool(results),
            "latencia_ms": int((time.time() - t0) * 1000),
            "enabled": True,
        },
        status=200,
    )
