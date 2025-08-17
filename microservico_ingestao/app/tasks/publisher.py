import json

from app.core.celery_app import celery_app


@celery_app.task(name="tasks.publisher.send_to_queue")
def send_to_queue(data: dict):
    """
    Publica os dados processados com JSON na fila 'processed_data'
    """

    message = json.dumps(data)
    print(
        f'[Celery Publisher] Mensagem enviada para fila processed_data: {message[:120]}...')
    return message
