from datetime import datetime

from apps.vendas.models import Compra
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

DATE_FMT = "%Y-%m-%d"


class VendaListView(LoginRequiredMixin, ListView):
    model = Compra
    template_name = "vendas/list.html"
    context_object_name = "vendas"
    paginate_by = 20

    def get_queryset(self):
        qs = (Compra.objects
              .select_related("cliente", "produto")
              .order_by("-data_hora"))

        q = (self.request.GET.get("q") or "").strip()
        forma = (self.request.GET.get("forma") or "").strip().upper()
        data_ini = (self.request.GET.get("data_ini") or "").strip()
        data_fim = (self.request.GET.get("data_fim") or "").strip()

        if q:
            qs = qs.filter(
                Q(cliente__nome__icontains=q) |
                Q(cliente__email__icontains=q) |
                Q(produto__nome__icontains=q) |
                Q(id_mensagem__icontains=q)
            )
        if forma:
            qs = qs.filter(forma_pagamento=forma)

        try:
            if data_ini:
                di = datetime.strptime(data_ini, DATE_FMT)
                qs = qs.filter(data_hora__date__gte=di.date())
            if data_fim:
                df = datetime.strptime(data_fim, DATE_FMT)
                qs = qs.filter(data_hora__date__lte=df.date())
        except ValueError:
            pass  # formato inválido: ignora

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["forma"] = self.request.GET.get("forma", "")
        ctx["data_ini"] = self.request.GET.get("data_ini", "")
        ctx["data_fim"] = self.request.GET.get("data_fim", "")
        return ctx
