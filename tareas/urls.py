from django.urls import path
from .views import disparar_suma, disparar_tarea_lenta, resultado_tarea, ejemplo_cache

urlpatterns = [
    path("sumar/", disparar_suma),
    path("lenta/", disparar_tarea_lenta),
    path("resultado/<str:task_id>/", resultado_tarea),
    path("cache/", ejemplo_cache),
]

