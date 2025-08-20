from apps.produtos.models import Produto
from apps.produtos.selectors import produtos_filtered_qs
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from utils.exports.mixins import ExportActionsMixin


class ProdutoListView(ExportActionsMixin, LoginRequiredMixin, ListView):
    model = Produto
    template_name = "produtos/list.html"
    context_object_name = "produtos"
    paginate_by = 20

    export_csv_url_name = "produtos:export_csv"
    export_pdf_url_name = "produtos:export_pdf"

    def get_queryset(self):
        return produtos_filtered_qs(self.request.GET)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["ativo"] = self.request.GET.get("ativo", "")
        ctx["title"] = "Produtos"
        ctx["subtitle"] = "Listagem e relatórios"
        return ctx
