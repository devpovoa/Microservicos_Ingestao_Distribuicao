from apps.produtos.models import Produto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.views.generic import ListView


class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "produtos/list.html"
    context_object_name = "produtos"
    paginate_by = 20

    def get_queryset(self):
        qs = (Produto.objects
              .annotate(qte_vendida=Sum("compras__quantidade"))
              .order_by("nome"))
        q = (self.request.GET.get("q") or "").strip()
        ativo = self.request.GET.get("ativo")  # "sim", "nao", None
        if q:
            qs = qs.filter(Q(nome__icontains=q))
        if ativo == "sim":
            qs = qs.filter(ativo=True)
        elif ativo == "nao":
            qs = qs.filter(ativo=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["ativo"] = self.request.GET.get("ativo", "")
        return ctx
