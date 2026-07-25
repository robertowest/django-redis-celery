from django.core.cache import cache
from django.test import TestCase

from config.celery import app as celery_app

from .tasks import sumar, tarea_lenta


class TareasTaskTests(TestCase):
    def test_sumar_devuelve_la_suma(self):
        self.assertEqual(sumar(5, 7), 12)

    def test_tarea_lenta_devuelve_mensaje_con_los_segundos(self):
        self.assertEqual(tarea_lenta(0), "Terminada en 0 segundos")


class DispararSumaViewTests(TestCase):
    def setUp(self):
        # config_from_object lee la config una sola vez, así que las tareas
        # deben ejecutarse en modo eager tocando la conf de Celery directamente
        # (override_settings de Django no llega hasta aquí). `store_eager_result`
        # además se congela en la clase de la tarea la primera vez que se vincula
        # a la app, así que hay que fijarlo ahí directamente y no solo en conf.
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True
        sumar.store_eager_result = True

    def tearDown(self):
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False
        sumar.store_eager_result = False

    def test_devuelve_task_id_y_el_resultado_correcto(self):
        response = self.client.get("/sumar/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["estado"], "en cola")
        self.assertIn("task_id", data)

        resultado = self.client.get(f"/resultado/{data['task_id']}/").json()
        self.assertEqual(resultado["estado"], "SUCCESS")
        self.assertEqual(resultado["resultado"], 12)


class DispararTareaLentaViewTests(TestCase):
    def test_devuelve_task_id_sin_esperar_a_que_termine(self):
        response = self.client.get("/lenta/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["estado"], "en cola")
        self.assertIn("task_id", data)


class ResultadoTareaViewTests(TestCase):
    def test_task_id_desconocido_devuelve_resultado_none(self):
        response = self.client.get("/resultado/id-inexistente/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["task_id"], "id-inexistente")
        self.assertIsNone(data["resultado"])


class EjemploCacheViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_genera_el_valor_y_lo_reutiliza_en_la_siguiente_llamada(self):
        primera = self.client.get("/cache/")
        self.assertEqual(primera.status_code, 200)
        self.assertEqual(
            primera.json(), {"mensaje": "generado y guardado en Redis"}
        )

        segunda = self.client.get("/cache/")
        self.assertEqual(segunda.json(), primera.json())
