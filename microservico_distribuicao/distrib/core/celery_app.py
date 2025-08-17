import os

from celery import Celery

# Garantia que o Django settings esteja visível ao Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery_app = Celery("distrib")

# Lê configurações do Django (definir as CELERY_* no settings)
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre automaticamente tasks em apps Django e pacotes listados
celery_app.autodiscover_tasks()

# (Opcional) sanity check ao iniciar


@celery_app.task(bind=True)
def ping(self):
    return 'pong'
