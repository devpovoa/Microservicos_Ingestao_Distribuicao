from apps.produtos.models import Produto
from apps.vendas.models import Compra
from django.db.models import (DateTimeField, DecimalField, OuterRef, Q,
                              Subquery, Sum)


def produtos_base_qs():
    # subqueries da última venda do produto
    last_price_sq = (Compra.objects
                     .filter(produto=OuterRef("pk"))
                     .order_by("-data_hora")
                     .values("preco_unitario")[:1])

    last_date_sq = (Compra.objects
                    .filter(produto=OuterRef("pk"))
                    .order_by("-data_hora")
                    .values("data_hora")[:1])

    return (Produto.objects
            .annotate(
                qte_vendida=Sum("compras__quantidade"),
                preco_recente=Subquery(last_price_sq, output_field=DecimalField(
                    max_digits=12, decimal_places=2)),
                ultima_venda=Subquery(
                    last_date_sq, output_field=DateTimeField()),
            ))


def produtos_filtered_qs(params):
    qs = produtos_base_qs().order_by("nome")
    q = (params.get("q") or "").strip()
    ativo = params.get("ativo")  # "sim", "nao", None
    if q:
        qs = qs.filter(Q(nome__icontains=q))
    if ativo == "sim":
        qs = qs.filter(ativo=True)
    elif ativo == "nao":
        qs = qs.filter(ativo=False)
    return qs
