import json
import logging

from apps.vendas.services import persist_compra_from_dto
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
    try:
        data = json.loads(payload) if isinstance(payload, str) else payload
        missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
        if missing:
            logger.warning(
                "Payload sem chaves de topo: %s; recebidas: %s", missing, list(data.keys()))

        dto = parse_payload(data)
        dto["id_mensagem"] = make_idempotency_key(dto)

        compra = persist_compra_from_dto(dto)

        logger.info(
            "Compra persistida. id_mensagem=%s cliente=%s produto=%s qte=%s total=%s data=%s",
            dto["id_mensagem"],
            compra.cliente.cpf_cnpj or f"{compra.cliente.nome}|{compra.cliente.email}",
            compra.produto.nome,
            compra.quantidade,
            str(compra.valor_total),
            compra.data_hora.isoformat(),
        )

        return {
            "status": "ok",
            "id_mensagem": compra.id_mensagem,
            "compra_id": compra.id,
            "cliente_id": compra.cliente_id,
            "produto_id": compra.produto_id,
        }
    except Exception as exc:
        logger.exception(
            "Falha ao persistir payload de processed_data: %s", exc)
        raise


# Alias/compat: delega para a task principal
@shared_task(name="tasks.publisher.send_to_queue")
def receive_from_ingest(payload: dict | str):
    return persist_processed_data(payload)
