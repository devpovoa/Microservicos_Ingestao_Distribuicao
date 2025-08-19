from django.urls import path

from .views.list import ClienteListView

urlpatterns = [
    path("", ClienteListView.as_view(), name="list"),
]
