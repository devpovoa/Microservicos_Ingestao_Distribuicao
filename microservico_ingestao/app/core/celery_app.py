from celery import Celery
from app.core.config import settings


celery_app = Celery(
    "ingest_service",
    broker=settings.rabbitmq_url,
    backend="rpc://"
)

celery_app.conf.task_routes = {
    "tasks.publisher.send_to_queue": {"queue": "processed_data"},
}

celery_app.conf.update(
    task_serializer = "json",
    accept_content = ["json"],
    result_serializer = "json",
    timezone = "America/Sao_Paulo",
    enable_utc = True,
)
