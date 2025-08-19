from django.urls import path

from .views.home import DashboardHome

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHome.as_view(), name="home"),
]
