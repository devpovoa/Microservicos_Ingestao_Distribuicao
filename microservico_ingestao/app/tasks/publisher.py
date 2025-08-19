import os

from celery import Celery

BROKER_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")

# Cliente Celery só para publicar
celery_client = Celery(__name__, broker=BROKER_URL)
celery_client.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue="processed_data",
)


def publish_processed_data(payload: dict) -> str:
    """
    Publica o payload normalizado para o consumidor (Django) na fila processed_data.
    Retorna o task_id.
    """
    res = celery_client.send_task(
        "workers.tasks.persist_processed_data",     # task do Django
        kwargs={"payload": payload},
        queue="processed_data",
        exchange="default",                         # casa com o worker
        routing_key="processed_data",
    )
    return res.id
