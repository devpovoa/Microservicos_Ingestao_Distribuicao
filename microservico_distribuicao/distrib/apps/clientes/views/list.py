from apps.clientes.models import Cliente
from apps.clientes.selectors import clientes_filtered_qs
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from utils.exports.mixins import ExportActionsMixin


class ClienteListView(ExportActionsMixin, LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"
    paginate_by = 20

    export_csv_url_name = "clientes:export_csv"
    export_pdf_url_name = "clientes:export_pdf"

    def get_queryset(self):
        return clientes_filtered_qs(self.request.GET)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["has_email"] = self.request.GET.get("has_email", "")
        return ctx
