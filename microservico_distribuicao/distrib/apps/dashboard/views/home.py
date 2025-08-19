from datetime import date, timedelta

from apps.vendas.selectors import (kpis_periodo, serie_mensal_12m,
                                   top_produtos_no_mes)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardHome(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        today = date.today()
        inicio_mes = today.replace(day=1)
        inicio_ano = today.replace(month=1, day=1)

        kpis_mes = kpis_periodo(inicio_mes, today + timedelta(days=1))
        kpis_ano = kpis_periodo(inicio_ano, today + timedelta(days=1))

        serie = serie_mensal_12m()
        top5 = top_produtos_no_mes(limit=5)

        ctx.update({
            "kpis_mes": kpis_mes,
            "kpis_ano": kpis_ano,
            "serie_labels": [p["label"] for p in serie],
            "serie_values": [float(p["total"]) for p in serie],
            "top_labels": [p["produto"] for p in top5],
            "top_values": [float(p["receita"]) for p in top5],
        })
        return ctx
