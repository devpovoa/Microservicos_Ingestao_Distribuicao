from datetime import datetime

from apps.vendas.models import Compra
from apps.vendas.selectors import iter_vendas_rows
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.views import View
from utils.exports.csv import stream_csv
from utils.exports.pdf import build_pdf_vendas

DATE_FMT = "%Y-%m-%d"


class VendasExportCSVView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = (Compra.objects
              .select_related("cliente", "produto")
              .order_by("-data_hora"))

        q = (request.GET.get("q") or "").strip()
        forma = (request.GET.get("forma") or "").strip().upper()
        data_ini = (request.GET.get("data_ini") or "").strip()
        data_fim = (request.GET.get("data_fim") or "").strip()

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
            pass

        headers = (
            "Data",
            "Cliente",
            "Documento",
            "Código Produto",
            "Produto",
            "Quantidade",
            "Preço Unitário",
            "Valor Total",
        )
        rows = iter_vendas_rows(qs)
        return stream_csv("vendas.csv", headers, rows, delimiter=";")


class VendasExportPDFView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = (Compra.objects
              .select_related("cliente", "produto")
              .order_by("-data_hora"))

        q = (request.GET.get("q") or "").strip()
        forma = (request.GET.get("forma") or "").strip().upper()
        data_ini = (request.GET.get("data_ini") or "").strip()
        data_fim = (request.GET.get("data_fim") or "").strip()

        if q:
            qs = qs.filter(
                Q(cliente__nome__icontains=q) |
                Q(cliente__email__icontains=q) |
                Q(produto__nome__icontains=q) |
                Q(id_mensagem__icontains=q)
            )
        if forma:
            qs = qs.filter(forma_pagamento=forma)

        periodo_txt = ""
        try:
            if data_ini:
                di = datetime.strptime(data_ini, DATE_FMT)
                qs = qs.filter(data_hora__date__gte=di.date())
                periodo_txt += f" de {di.strftime('%d/%m/%Y')}"
            if data_fim:
                df = datetime.strptime(data_fim, DATE_FMT)
                qs = qs.filter(data_hora__date__lte=df.date())
                periodo_txt += f" até {df.strftime('%d/%m/%Y')}"
        except ValueError:
            pass

        # KPIs do queryset filtrado
        aggs = qs.aggregate(total=Sum("valor_total"), qtd=Count("id"))
        total = aggs.get("total") or 0
        qtd = aggs.get("qtd") or 0
        ticket = (total / qtd) if qtd else 0
        kpis = {"total": total, "qtd": qtd, "ticket": ticket}

        headers = (
            "Data",
            "Cliente",
            "Documento",
            "Código Produto",
            "Produto",
            "Quantidade",
            "Preço Unitário",
            "Valor Total",
        )
        rows = iter_vendas_rows(qs)

        title = "Relatório de Vendas"
        subtitle = f"Filtros aplicados{periodo_txt}" if periodo_txt else "Filtros aplicados: (sem período)"
        pdf_bytes = build_pdf_vendas(title, subtitle, kpis, headers, rows)

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="vendas.pdf"'
        return resp
