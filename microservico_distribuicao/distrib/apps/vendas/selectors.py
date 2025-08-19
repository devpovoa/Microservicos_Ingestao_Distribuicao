from calendar import month_name
from datetime import date, datetime

from django.db.models import Count, Sum
from django.utils import timezone

from .models import Compra


def total_vendas_periodo(inicio: datetime, fim: datetime):
    return (Compra.objects
            .filter(data_hora__gte=inicio,
                    data_hora__lt=fim)
            .aaggregate(total=Sum("valor_total"))["total"] or 0
            )


def top_produtos_periodo(inicio: datetime, fim: datetime, limit: int = 5):
    return (Compra.objects
            .filter(data_hora__gte=inicio, data_hora__lt=fim)
            .values("produto__nome")
            .annotate(qte=Sum("quantidade"), vendas=Sum("valor_total"))
            .order_by("-qte")[:limit]
            )


def kpis_periodo(inicio, fim):
    qs = Compra.objects.filter(data_hora__gte=inicio, data_hora__lt=fim)
    total = qs.aggregate(total=Sum("valor_total"))["total"] or 0
    qtd = qs.aggregate(qtd=Count("id"))["qtd"] or 0
    ticket = (total / qtd) if qtd else 0
    return {"total": total, "qtd": qtd, "ticket": ticket}


def _month_label(d: date):
    # ex.: Jan/2025
    return f"{month_name[d.month][:3]}/{d.year}"


def serie_mensal_12m():
    """Soma por mês nos últimos 12 meses (inclui mês atual)."""
    today = timezone.localdate()
    # constrói a lista de 12 meses (do mais antigo ao atual)
    months = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months = list(reversed(months))

    points = []
    for y, m in months:
        start = date(y, m, 1)
        # início do mês seguinte
        if m == 12:
            end = date(y+1, 1, 1)
        else:
            end = date(y, m+1, 1)
        total = (Compra.objects
                 .filter(data_hora__gte=start, data_hora__lt=end)
                 .aggregate(total=Sum("valor_total"))["total"] or 0)
        points.append({"label": _month_label(start), "total": total})
    return points


def top_produtos_no_mes(limit=5):
    """Top produtos por receita no mês corrente."""
    today = timezone.localdate()
    start = today.replace(day=1)
    end = (start.replace(month=start.month % 12 + 1, year=start.year + (start.month // 12))
           if start.month < 12 else date(start.year + 1, 1, 1))
    rows = (Compra.objects
            .filter(data_hora__gte=start, data_hora__lt=end)
            .values("produto__nome")
            .annotate(receita=Sum("valor_total"))
            .order_by("-receita")[:limit])
    return [{"produto": r["produto__nome"], "receita": r["receita"] or 0} for r in rows]
