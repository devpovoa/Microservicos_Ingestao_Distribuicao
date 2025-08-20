# distrib/apps/clientes/exports.py
from typing import Iterator, Tuple

HEADERS = ("Cliente", "Documento", "Email", "Compras", "Receita (R$)",
           "Ticket médio (R$)", "Última compra", "Criado em")


def _fmt_money(val):
    if not val:
        return "0,00"
    try:
        return f"{float(val):.2f}".replace(".", ",")
    except Exception:
        return str(val)


def iter_rows(queryset) -> Iterator[Tuple]:
    for c in queryset.iterator(chunk_size=2000):
        qtd = getattr(c, "qtd_compras", 0) or 0
        receita = getattr(c, "receita_total", 0) or 0
        ticket = (float(receita) / float(qtd)) if qtd else 0.0

        ultima = c.ultima_compra.strftime(
            "%d/%m/%Y %H:%M") if getattr(c, "ultima_compra", None) else ""
        criado = c.created_at.strftime(
            "%d/%m/%Y %H:%M") if getattr(c, "created_at", None) else ""

        yield (
            getattr(c, "nome", ""),
            getattr(c, "cpf_cnpj", ""),
            getattr(c, "email", ""),
            qtd,
            _fmt_money(receita),
            _fmt_money(ticket),
            ultima,
            criado,
        )
