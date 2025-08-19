from django.urls import path

from .views.list import ProdutoListView

urlpatterns = [
    path("", ProdutoListView.as_view(), name="list"),
]
