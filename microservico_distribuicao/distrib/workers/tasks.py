import json
import logging

from celery import shared_task

from .idempotency import make_idempotency_key
from .parsers import parse_payload

logger = logging.getLogger(__name__)

REQUIRED_TOP_LEVEL_KEYS = {
    "cliente",
    "produto",
    "quantidade",
    "valor_unitario",
    "valor_total",
    "data_hora",
    "forma_pagamento",
}


@shared_task(name="workers.tasks.persist_processed_data")
def persist_processed_data(payload: dict | str):
    """
    Recebe uma compra (dict ou JSON str), valida/normaliza e
    PREPARA para persistência (próxima subetapa da Etapa 5).

    Retorna metadados úteis para logs/observabilidade.
    """
    try:
        data = json.loads(payload) if isinstance(payload, str) else payload

        # Alerta amigável caso falte algo do topo (não bloqueia parse_payload, que valida de fato)
        missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
        if missing:
            logger.warning(
                "Payload sem chaves obrigatórias de topo: %s; recebidas: %s",
                missing, list(data.keys())
            )

        # Normaliza e valida
        dto = parse_payload(data)
        dto["id_mensagem"] = make_idempotency_key(dto)

        # Aqui, na próxima subetapa, chamaremos um service de domínio
        # (ex.: services.persist_compra(dto)) que fará a transação atômica.

        logger.info(
            "Payload validado. id_mensagem=%s cliente=%s produto=%s qte=%s total=%s data=%s",
            dto["id_mensagem"],
            dto["cliente"]["cpf_cnpj"] or f"{dto['cliente']['nome']}|{dto['cliente']['email']}",
            dto["produto"]["nome"],
            dto["quantidade"],
            str(dto["valor_total"]),
            dto["data_hora"].isoformat(),
        )

        return {
            "status": "ok",
            "id_mensagem": dto["id_mensagem"],
            "cliente_ref": dto["cliente"]["cpf_cnpj"] or dto["cliente"]["email"],
            "produto": dto["produto"]["nome"],
        }
    except Exception as exc:
        logger.exception(
            "Falha ao processar payload de processed_data: %s", exc)
        raise


# Alias/compat: delega para a task principal
@shared_task(name="tasks.publisher.send_to_queue")
def receive_from_ingest(payload: dict | str):
    return persist_processed_data(payload)
