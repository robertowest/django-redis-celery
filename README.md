# redis-celery

Proyecto de aprendizaje/demo que integra **Django**, **Celery** y **Redis** para mostrar cómo ejecutar tareas asíncronas en segundo plano y usar Redis como cache y backend de sesiones.

## Estructura del proyecto

```
redis-celery/
├─ manage.py
├─ requirements.txt
├─ .env
├─ config/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ celery.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
└─ tareas/
   ├─ __init__.py
   ├─ apps.py
   ├─ tasks.py
   ├─ urls.py
   └─ views.py
```

## ¿Qué hace?

- Expone unas vistas HTTP muy simples que lanzan tareas de Celery (una suma, una tarea "lenta" que tarda varios segundos, y el envío de un email) y permiten consultar el resultado de esas tareas por su `task_id`.
- Usa Redis como:
  - **Broker** de Celery (cola de mensajes de tareas).
  - **Result backend** de Celery (donde se guarda el resultado de cada tarea).
  - **Cache** de Django (`django_redis`).
  - **Backend de sesiones** de Django (las sesiones se guardan en la cache, es decir, en Redis).

## Estructura

```
config/             # Proyecto Django: settings, urls, arranque de Celery
tareas/             # App Django con las tareas de Celery y las vistas de ejemplo
docker-compose.yml  # Levanta un contenedor de Redis para desarrollo
requirements.txt    # Dependencias del proyecto
```

Piezas clave:
```
config/celery.py    # crea la app de Celery y la conecta con la configuración de Django (`CELERY_*` en `settings.py`).
config/__init__.py  # expone `celery_app` para que las tareas (`@shared_task`) se registren correctamente.
tareas/tasks.py     # las tareas: `sumar`, `tarea_lenta`, `enviar_email`.
tareas/views.py     # vistas que disparan las tareas y consultan resultados/cache.
```

## Requisitos

- Python 3 (entorno virtual con las dependencias de `requirements.txt`).
- Docker (para levantar Redis con `docker-compose.yml`).

## Puesta en marcha

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Copiar/ajustar variables de entorno en `.env` (ya incluye valores por defecto para desarrollo):
   ```
   DEBUG=1
   SECRET_KEY=...
   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
   REDIS_URL=redis://127.0.0.1:6379/0
   REDIS_RESULT_URL=redis://127.0.0.1:6379/1
   ```

3. Levantar Redis:
   ```bash
   docker compose up -d redis
   ```

4. Aplicar migraciones:
   ```bash
   python manage.py migrate
   ```

5. Arrancar el servidor Django:
   ```bash
   python manage.py runserver
   ```

6. En otra terminal, arrancar el worker de Celery:
   ```bash
   celery -A config worker -l info
   ```

## Endpoints de prueba

| Endpoint | Qué hace |
|---|---|
| `GET /sumar/` | Lanza la tarea `sumar(5, 7)` en segundo plano y devuelve su `task_id`. |
| `GET /lenta/` | Lanza `tarea_lenta(10)` (tarda 10s en el worker) y devuelve el `task_id` al instante. |
| `GET /resultado/<task_id>/` | Consulta el estado/resultado de una tarea por su id. |
| `GET /cache/` | Genera un valor la primera vez y lo guarda en Redis (cache) 60s; en llamadas posteriores lo sirve desde ahí. |

## Notas

- El envío de email (`enviar_email`) usa por defecto el backend de consola (`EMAIL_BACKEND`), así que en desarrollo el correo se imprime en la terminal del worker en vez de enviarse de verdad.
- Los endpoints de ejemplo son `GET` y públicos (sin autenticación) — válido para practicar, pero no para producción.
