from typing import Iterator, Tuple

HEADERS = ("Produto", "Preço recente", "Qtd. vendida",
           "Última venda", "Criado em")


def _fmt_brl(val):
    if val is None:
        return ""
    try:
        return f"{float(val):.2f}".replace(".", ",")
    except Exception:
        return str(val)


def iter_rows(queryset) -> Iterator[Tuple]:
    for p in queryset.iterator(chunk_size=2000):
        nome = getattr(p, "nome", "")
        preco = _fmt_brl(getattr(p, "preco_recente", None))
        qte = getattr(p, "qte_vendida", 0) or 0
        ultima = p.ultima_venda.strftime(
            "%d/%m/%Y %H:%M") if getattr(p, "ultima_venda", None) else ""
        criado = p.created_at.strftime(
            "%d/%m/%Y %H:%M") if getattr(p, "created_at", None) else ""
        yield (nome, preco, qte, ultima, criado)
