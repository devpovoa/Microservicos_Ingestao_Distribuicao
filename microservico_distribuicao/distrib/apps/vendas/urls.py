# distrib/apps/vendas/urls.py
from django.urls import path

from .views.list import VendaListView

app_name = "vendas"

urlpatterns = [
    path("", VendaListView.as_view(), name="list"),
]
