from apps.clientes.exports import HEADERS, iter_rows
from apps.clientes.selectors import clientes_filtered_qs
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View
from utils.exports.csv import stream_csv
from utils.exports.pdf import build_pdf_table


class ClientesExportCSVView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = clientes_filtered_qs(request.GET)
        return stream_csv("clientes.csv", HEADERS, iter_rows(qs), delimiter=";")


class ClientesExportPDFView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        qs = clientes_filtered_qs(request.GET)
        pdf = build_pdf_table("Relatório de Clientes",
                              None, HEADERS, iter_rows(qs))
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="clientes.pdf"'
        return resp
