from django.urls import path
from .views import RegisterView, ProfileView, DashboardView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("users/me/", ProfileView.as_view(), name="me"),
    path("users/dashboard/", DashboardView.as_view(), name="dashboard"),
]
