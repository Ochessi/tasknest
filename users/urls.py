from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, DashboardView,
    PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView,
    SecurityView, health_check
)

urlpatterns = [
    # Authentication endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Password management
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
    
    # User profile and dashboard
    path("me/", ProfileView.as_view(), name="profile"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("security/", SecurityView.as_view(), name="security"),
    
    # Health check
    path("health/", health_check, name="auth_health_check"),
]
