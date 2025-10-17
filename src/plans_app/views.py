import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Planificacion

ERR_AUTH = {'error': 'Authentication required'}
ERR_JSON = {'error': 'Invalid JSON'}
ERR_TITULO = {'error': 'Titulo is required'}


def _plan_to_dict(plan: Planificacion):
    return {
        'id': plan.id,
        'titulo': plan.titulo,
        'descripcion': plan.descripcion,
        'contenido': plan.contenido,
        'creado_en': plan.creado_en.isoformat(),
        'actualizado_en': plan.actualizado_en.isoformat(),
    }


@csrf_exempt
@require_http_methods(["GET"])
def mis_planificaciones(request):
    if not request.user.is_authenticated:
        return JsonResponse(ERR_AUTH, status=401)
    plans = Planificacion.objects.filter(owner=request.user)
    return JsonResponse({'results': [_plan_to_dict(p) for p in plans]}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def crear_planificacion(request):
    if not request.user.is_authenticated:
        return JsonResponse(ERR_AUTH, status=401)
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse(ERR_JSON, status=400)

    titulo = (payload.get('titulo') or '').strip()
    descripcion = payload.get('descripcion') or ''
    contenido = payload.get('contenido') or {}
    if not titulo:
        return JsonResponse(ERR_TITULO, status=400)

    plan = Planificacion.objects.create(
        owner=request.user,
        titulo=titulo,
        descripcion=descripcion,
        contenido=contenido,
    )
    return JsonResponse(_plan_to_dict(plan), status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def planificacion_detalle(request, plan_id: int):
    if not request.user.is_authenticated:
        return JsonResponse(ERR_AUTH, status=401)
    plan = get_object_or_404(Planificacion, id=plan_id, owner=request.user)

    if request.method == 'GET':
        return JsonResponse(_plan_to_dict(plan))

    if request.method == 'PATCH':
        return _patch_plan(request, plan)

    if request.method == 'DELETE':
        plan.delete()
        return JsonResponse({'message': 'Deleted'})

    return HttpResponseNotAllowed(["GET", "PATCH", "DELETE"])


def _patch_plan(request, plan: Planificacion):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse(ERR_JSON, status=400)
    if 'titulo' in payload:
        t = (payload.get('titulo') or '').strip()
        if not t:
            return JsonResponse(ERR_TITULO, status=400)
        plan.titulo = t
    if 'descripcion' in payload:
        plan.descripcion = payload.get('descripcion') or ''
    if 'contenido' in payload:
        plan.contenido = payload.get('contenido') or {}
    plan.save()
    return JsonResponse(_plan_to_dict(plan))
