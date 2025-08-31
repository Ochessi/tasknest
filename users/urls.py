from django.urls import path
from .views import RegisterView, ProfileView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("users/me/", ProfileView.as_view(), name="me"),
]
