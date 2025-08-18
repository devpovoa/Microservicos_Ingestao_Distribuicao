from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.utils import timezone

_CLEAN_DIGITS = re.compile(r"\D+")


def _only_digits(s: str | None):
    # Remove tudo que não for dígito: mantém None se vazio.
    if not s:
        return s
    return _CLEAN_DIGITS.sub("", s)


def parse_payload(payload: dict | str):
    # Normaliza o JSON de entrada no formato interno (DTO).

    data = json.loads(payload) if isinstance(payload, str) else payload

    # Cliente
    c = data.get("cliente") or {}
    cliente = {
        "nome": (c.get("nome") or "").strip(),
        "email": (c.get("email") or "").strip().lower(),
        "telefone": _only_digits(c.get("telefone")),
        "cpf_cnpj": _only_digits(c.get("cpf_cnpj")),
        "endereco_completo": (c.get("endereco_completo") or "").strip(),
    }

    # Produto
    p = data.get("produto") or {}
    nome_produto = (p.get("nome_produto") or "").strip()
    produto = {"nome": nome_produto}

    # Numéricos
    try:
        quantidade = int(data.get("quantidade"))
        if quantidade <= 0:
            raise ValueError("quantidade deve ser > 0")
    except Exception:
        raise ValueError("quantidade inválida (inteiro > 0 esperado)")

    try:
        valor_unitario = Decimal(str(data.get("valor_unitario")))
        valor_total = Decimal(str(data.get("valor_total")))
    except (InvalidOperation, TypeError):
        raise ValueError(
            "valor_unitario/valor_total inválido (Decimal esperado)")

    # Data/hora
    raw_dt = data.get("data_hora")
    if not raw_dt:
        raise ValueError("data_hora ausente")

    try:
        dt = datetime.fromisoformat(str(raw_dt).replace("Z", "+00:00"))
        data_hora = dt if dt.tzinfo else timezone.make_aware(
            dt, timezone.get_current_timezone())
    except Exception:
        raise ValueError("data_hora inválida (ISO-8601 esperado)")

    forma_pagamento = (data.get("forma_pagamento") or "").strip()
    if not forma_pagamento:
        forma_pagamento = "OUTROS"

    # Valida mínimos essenciais
    if not produto["nome"]:
        raise ValueError("produto.nome_produto vazio")
    if not cliente["nome"]:
        raise ValueError("cliente.nome vazio")

    # Precisa ter pelo menos cpf_cnpj ou email para identificação
    if not (cliente["cpf_cnpj"] or cliente["email"]):
        raise ValueError("informe ao menos cpf_cnpj ou email do cliente")

    return {
        "cliente": cliente,
        "produto": produto,
        "quantidade": quantidade,
        "valor_unitario": valor_unitario,
        "valor_total": valor_total,
        "data_hora": data_hora,
        "forma_pagamento": forma_pagamento,
    }
