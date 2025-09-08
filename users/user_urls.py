from django.urls import path
from .views import ProfileView, DashboardView

urlpatterns = [
    path("me/", ProfileView.as_view(), name="me"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
