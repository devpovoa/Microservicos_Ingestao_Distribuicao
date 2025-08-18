import hashlib


def make_purchase_fprint(dto: dict):
    # Monta uma 'impressão digital' estável para a compra.

    c = dto["cliente"]
    p = dto["produto"]
    parts = [
        c.get("cpf_cnpj") or "",
        c.get("email") or "",
        p["nome"],
        str(dto["quantidade"]),
        str(dto["valor_unitario"]),
        str(dto["valor_total"]),
        dto["data_hora"].isoformat(),
        (dto.get("forma_pagamento") or "").upper(),
    ]

    return "|".join(parts)


def make_idempotency_key(dto: dict):
    # Aplica SHA-256
    fprint = make_purchase_fprint(dto)
    return hashlib.sha256(fprint.encode("utf-8")).hexdigest()
