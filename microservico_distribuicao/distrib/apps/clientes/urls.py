from django.urls import path

from .views.export import ClientesExportCSVView, ClientesExportPDFView
from .views.list import ClienteListView

app_name = "clientes"

urlpatterns = [
    path("", ClienteListView.as_view(), name="list"),
    path("export/csv/", ClientesExportCSVView.as_view(), name="export_csv"),
    path("export/pdf/", ClientesExportPDFView.as_view(), name="export_pdf"),
]
