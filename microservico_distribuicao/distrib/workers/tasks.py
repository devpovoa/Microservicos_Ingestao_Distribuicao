import json
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="workers.tasks.persist_processed_data")
def persist_processed_data(payload: dict | str):
    """
    Aceita payload como dict ou string JSON
    """
    try:
        data = json.loads(payload) if isinstance(payload, str) else payload
        # Validação mínima (incremental): esperamos chaves de alto nível
        # Ajuste de acordo com o microserviço 1 publica
        excepted_keys = {"cliente", "produtos", "compras"}
        if not excepted_keys.intersection(set(map(str.lower, data.keys()))):
            logger.warning(
                f"Payload recebido sem chaves esperadas: {list(data.keys())}")
        else:
            logger.info(
                f"Payload recebido OK. Tamanho aproximado: {len(json.dumps(data))} bytes.")

        return {"status": "ok", "received_keys": list(data.keys())}
    except Exception as exc:
        logger.exception(
            f"Falha ao processar payload de processed_data: {exc}")
        raise

# Registramos um alias que apenas delega para a task oficial acima.


@shared_task(name="tasks.publisher.send_to_queue")
def receive_from_ingest(payload: dict | str):
    return persist_processed_data(payload)
