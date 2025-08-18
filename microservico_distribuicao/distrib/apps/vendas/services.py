from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from apps.clientes.models import Cliente, Endereco
from apps.produtos.models import Produto
from django.db import IntegrityError, transaction

from .choices import FORMA_PAGAMENTO_CHOICES, OUTROS
from .models import Compra


@transaction.atomic
def persist_compra_from_dto(dto: Dict[str, Any]) -> Compra:
    """
    Persiste uma compra a partir do DTO já normalizado pelo workers.parsers.
    Garante idempotência via id_mensagem (unique).
    """
    c = dto["cliente"]
    p = dto["produto"]

    # ----- Cliente -----
    cliente = None
    if c.get("cpf_cnpj"):
        cliente, _ = Cliente.objects.get_or_create(
            cpf_cnpj=c["cpf_cnpj"],
            defaults={
                "nome": c["nome"],
                "email": c.get("email") or None,
                "telefone": c.get("telefone") or None,
            },
        )
        # Pode atualizar dados novos sem sobrescrever agressivamente
        changed = False
        if c.get("email") and c["email"] != (cliente.email or ""):
            cliente.email = c["email"]
            changed = True
        if c.get("telefone") and c["telefone"] != (cliente.telefone or ""):
            cliente.telefone = c["telefone"]
            changed = True
        if c["nome"] and c["nome"] != cliente.nome:
            cliente.nome = c["nome"]
            changed = True
        if changed:
            cliente.save(update_fields=["nome", "email", "telefone"])
    else:
        # Fallback por (nome, email)
        cliente, _ = Cliente.objects.get_or_create(
            nome=c["nome"],
            email=c.get("email") or None,
            defaults={"telefone": c.get("telefone") or None},
        )

    # ----- Endereço (opcional) -----
    endereco_texto = (c.get("endereco_completo") or "").strip()
    if endereco_texto:
        Endereco.objects.get_or_create(
            cliente=cliente, endereco_completo=endereco_texto)

    # ----- Produto -----
    produto, _ = Produto.objects.get_or_create(nome=p["nome"])

    # ----- Compra (idempotência) -----
    id_mensagem = dto["id_mensagem"]
    forma = (dto.get("forma_pagamento") or OUTROS).upper()
    if forma not in dict(FORMA_PAGAMENTO_CHOICES):
        forma = OUTROS

    try:
        compra, created = Compra.objects.get_or_create(
            id_mensagem=id_mensagem,
            defaults={
                "cliente": cliente,
                "produto": produto,
                "quantidade": int(dto["quantidade"]),
                "preco_unitario": Decimal(dto["valor_unitario"]),
                "valor_total": Decimal(dto["valor_total"]),
                "forma_pagamento": forma,
                "data_hora": dto["data_hora"],
            },
        )
        return compra
    except IntegrityError:
        # Caso de corrida raro: alguém gravou a mesma id_mensagem no intervalo
        return Compra.objects.get(id_mensagem=id_mensagem)
