from celery import shared_task
from time import sleep
from django.core.mail import send_mail


@shared_task
def sumar(a, b):
    return a + b


@shared_task
def tarea_lenta(segundos=5):
    sleep(segundos)
    return f"Terminada en {segundos} segundos"


@shared_task
def enviar_email(destinatario):
    send_mail(
        "Bienvenido",
        "Gracias por registrarte",
        "noreply@tusitio.com",
        [destinatario],
    )


