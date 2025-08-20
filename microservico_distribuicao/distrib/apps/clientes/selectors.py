from apps.clientes.models import Cliente
from django.db.models import Count, Max, Q, Sum


def clientes_base_qs():
    return (Cliente.objects
            .annotate(
                # <- ajuste se necessário
                qtd_compras=Count("compras"),
                # <- ajuste se necessário
                receita_total=Sum("compras__valor_total"),
                # <- ajuste se necessário
                ultima_compra=Max("compras__data_hora"),
            ))


def clientes_filtered_qs(params):
    qs = clientes_base_qs().order_by("nome")
    q = (params.get("q") or "").strip()
    # se você tiver este campo/filtro; senão remova
    ativo = params.get("ativo")

    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(
            email__icontains=q) | Q(cpf_cnpj__icontains=q))

    # Se existir um campo "ativo" em Cliente e você quiser manter o filtro:
    if ativo == "sim":
        qs = qs.filter(ativo=True)
    elif ativo == "nao":
        qs = qs.filter(ativo=False)

    return qs
