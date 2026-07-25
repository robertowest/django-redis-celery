import json

from django.http import JsonResponse
from django.core.cache import cache
from .tasks import sumar, tarea_lenta


def disparar_suma(request):
    task = sumar.delay(5, 7)
    return JsonResponse({"task_id": task.id, "estado": "en cola"})


def disparar_tarea_lenta(request):
    task = tarea_lenta.delay(10)
    return JsonResponse({"task_id": task.id, "estado": "en cola"})


def resultado_tarea(request, task_id):
    from celery.result import AsyncResult
    r = AsyncResult(task_id)
    return JsonResponse({
        "task_id": task_id,
        "estado": r.status,
        "resultado": r.result if r.ready() else None,
    })


def ejemplo_cache(request):
    clave = "hola_celery"
    valor = cache.get(clave)
    if valor is None:
        valor = json.dumps({"mensaje": "generado y guardado en Redis"})
        cache.set(clave, valor, timeout=60)
    return JsonResponse(json.loads(valor))


