from datetime import datetime

from django.db.models import Count, F, Sum

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
