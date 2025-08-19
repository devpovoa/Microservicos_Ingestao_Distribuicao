from apps.clientes.models import Cliente
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import ListView


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"
    paginate_by = 20

    def get_queryset(self):
        qs = (Cliente.objects
              .annotate(total_compras=Count("compras"))
              .order_by("-created_at"))
        q = (self.request.GET.get("q") or "").strip()
        has_email = self.request.GET.get("has_email")
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(
                email__icontains=q) | Q(cpf_cnpj__icontains=q))
        if has_email == "1":
            qs = qs.exclude(email__isnull=True).exclude(email__exact="")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["has_email"] = self.request.GET.get("has_email", "")
        return ctx
