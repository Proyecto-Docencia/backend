# chat_app/views.py

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Chat, ChatSession
# Importamos la función del servicio de IA (Gemini)
from .ai_service import consultar_gemini
# Importamos RAG para búsqueda en PDFs
from rag_proxy.retrieval import search, format_context


@login_required
@require_http_methods(["GET"])
def mis_sesiones(request: HttpRequest):
    """Listar todas las sesiones de chat del usuario"""
    sesiones = ChatSession.objects.filter(user=request.user)
    data = [
        {
            "id": s.id,
            "titulo": s.titulo,
            "creado_en": s.creado_en.isoformat(),
            "actualizado_en": s.actualizado_en.isoformat(),
            "mensajes_count": s.mensajes.count(),
        }
        for s in sesiones
    ]
    return JsonResponse({"results": data}, status=200)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crear_sesion(request: HttpRequest):
    """Crear una nueva sesión de chat"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}
    
    titulo = payload.get("titulo", "Nueva conversación")
    sesion = ChatSession.objects.create(user=request.user, titulo=titulo)
    
    return JsonResponse({
        "id": sesion.id,
        "titulo": sesion.titulo,
        "creado_en": sesion.creado_en.isoformat(),
        "mensajes": [],
    }, status=201)


@login_required
@require_http_methods(["GET"])
def obtener_sesion(request: HttpRequest, sesion_id: int):
    """Obtener una sesión con todos sus mensajes"""
    sesion = get_object_or_404(ChatSession, id=sesion_id, user=request.user)
    mensajes = [
        {
            "id": m.id,
            "mensaje_usuario": m.mensaje_usuario,
            "respuesta_ia": m.respuesta_ia,
            "fecha": m.fecha.isoformat(),
        }
        for m in sesion.mensajes.all()
    ]
    
    return JsonResponse({
        "id": sesion.id,
        "titulo": sesion.titulo,
        "creado_en": sesion.creado_en.isoformat(),
        "actualizado_en": sesion.actualizado_en.isoformat(),
        "mensajes": mensajes,
    }, status=200)


@login_required
@require_http_methods(["GET"])
def mis_chats(request: HttpRequest):
    """LEGACY: Listar últimos chats (mantener compatibilidad)"""
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
    """Crear un mensaje en una sesión (con RAG si es necesario)"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    mensaje = (payload.get("mensaje_usuario") or "").strip()
    sesion_id = payload.get("sesion_id")
    usar_rag = payload.get("usar_rag", True)  # Por defecto usa RAG
    
    if not mensaje:
        return JsonResponse({"error": "mensaje_usuario requerido"}, status=400)

    # Obtener o crear sesión
    if sesion_id:
        try:
            sesion = ChatSession.objects.get(id=sesion_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({"error": "Sesión no encontrada"}, status=404)
    else:
        # Crear nueva sesión automáticamente
        primer_mensaje_titulo = mensaje[:50] + ("..." if len(mensaje) > 50 else "")
        sesion = ChatSession.objects.create(
            user=request.user,
            titulo=primer_mensaje_titulo
        )
    
    # ========================================
    # RAG: Buscar contexto en PDFs
    # ========================================
    contexto_rag = ""
    if usar_rag:
        try:
            resultados = search(mensaje, top_k=3)
            if resultados:
                contexto_rag = "\n\n**Contexto de documentos educativos:**\n"
                contexto_rag += format_context(resultados)
        except Exception as e:
            print(f"[RAG] Error al buscar documentos: {e}")
            # Continuar sin RAG si falla
    
    # ========================================
    # Construir prompt con contexto RAG
    # ========================================
    if contexto_rag:
        prompt_completo = f"""{contexto_rag}

**Pregunta del docente:** {mensaje}

Por favor, responde basándote en el contexto proporcionado de los documentos educativos."""
    else:
        prompt_completo = mensaje
    
    # ========================================
    # Consultar a Gemini
    # ========================================
    respuesta_modelo = consultar_gemini(prompt_completo)
    
    # ========================================
    # Guardar mensaje en la sesión
    # ========================================
    chat = Chat.objects.create(
        session=sesion,
        user=request.user,
        mensaje_usuario=mensaje,
        respuesta_ia=respuesta_modelo
    )
    
    # Actualizar timestamp de la sesión
    sesion.save()  # Esto actualiza 'actualizado_en'
    
    return JsonResponse({
        "id": chat.id,
        "sesion_id": sesion.id,
        "mensaje_usuario": chat.mensaje_usuario,
        "respuesta_ia": chat.respuesta_ia,
        "fecha": chat.fecha.isoformat(),
        "usado_rag": bool(contexto_rag),
    }, status=201)