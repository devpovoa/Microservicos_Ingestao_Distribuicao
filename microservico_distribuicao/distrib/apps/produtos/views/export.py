from apps.produtos.exports import HEADERS, iter_rows
from apps.produtos.selectors import produtos_filtered_qs
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View
from utils.exports.csv import stream_csv
from utils.exports.pdf import build_pdf_table


class ProdutosExportCSVView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = produtos_filtered_qs(request.GET)
        return stream_csv("produtos.csv", HEADERS, iter_rows(qs), delimiter=";")


class ProdutosExportPDFView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = produtos_filtered_qs(request.GET)
        pdf = build_pdf_table("Relatório de Produtos",
                              None, HEADERS, iter_rows(qs))
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="produtos.pdf"'
        return resp
