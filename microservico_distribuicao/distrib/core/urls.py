from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("clientes/", include(("apps.clientes.urls", "clientes"), namespace="clientes")),
    path("produtos/", include(("apps.produtos.urls", "produtos"), namespace="produtos")),
    path("vendas/", include(("apps.vendas.urls", "vendas"), namespace="vendas")),
    path("", include(("apps.dashboard.urls", "dashboard"),
         namespace="dashboard")),
]
