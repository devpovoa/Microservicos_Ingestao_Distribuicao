from django.urls import path

from .views.export import ProdutosExportCSVView, ProdutosExportPDFView
from .views.list import ProdutoListView

app_name = "produtos"

urlpatterns = [
    path("", ProdutoListView.as_view(), name="list"),
    path("export/csv/", ProdutosExportCSVView.as_view(), name="export_csv"),
    path("export/pdf/", ProdutosExportPDFView.as_view(), name="export_pdf"),
]
