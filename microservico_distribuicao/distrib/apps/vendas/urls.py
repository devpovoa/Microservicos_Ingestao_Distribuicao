from django.urls import path

from .views.export import VendasExportCSVView, VendasExportPDFView
from .views.list import VendaListView

app_name = "vendas"

urlpatterns = [
    path("", VendaListView.as_view(), name="list"),
    path("export/csv/", VendasExportCSVView.as_view(), name="export_csv"),
    path("export/pdf/", VendasExportPDFView.as_view(), name="export_pdf"),
]
