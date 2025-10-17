# chat_app/views.py

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Chat
# Importamos la función del servicio de IA (Gemini)
from .ai_service import consultar_gemini 


@login_required
@require_http_methods(["GET"])
def mis_chats(request: HttpRequest):
    # ... (Tu código actual para listar chats sigue igual)
    qs = Chat.objects.filter(user=request.user).order_by("-fecha")[:100]
    data = [
        {
            "id": c.id,
            "mensaje_usuario": c.mensaje_usuario,
            "respuesta_ia": c.respuesta_ia,
            "fecha": c.fecha.isoformat(),
        }
        for c in qs
    ]
    return JsonResponse({"results": data}, status=200)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crear_chat(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    mensaje = (payload.get("mensaje_usuario") or "").strip()
    if not mensaje:
        return JsonResponse({"error": "mensaje_usuario requerido"}, status=400)

    # ==========================================================
    # PASO CLAVE: CONSULTAR A LA IA LOCAL ANTES DE GUARDAR
    # ==========================================================
    
    # 1. Obtenemos la respuesta del modelo Gemini
    respuesta_modelo = consultar_gemini(mensaje)
    
    # 2. Creamos el objeto Chat, incluyendo la respuesta de la IA
    chat = Chat.objects.create(
        user=request.user, 
        mensaje_usuario=mensaje, 
        respuesta_ia=respuesta_modelo # <-- Usamos la respuesta generada
    )
    
    # 3. Devolvemos la respuesta, que ahora contiene la respuesta_ia real
    return JsonResponse({
        "id": chat.id,
        "mensaje_usuario": chat.mensaje_usuario,
        "respuesta_ia": chat.respuesta_ia, # <-- Este campo ya no está vacío
        "fecha": chat.fecha.isoformat(),
    }, status=201)