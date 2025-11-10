from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import admin_views

app_name = "auth_app"

urlpatterns = [
    # Auth endpoints
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("confirm-email/", views.ConfirmEmailView.as_view(), name="confirm-email"),
    path(
        "resend-confirmation/",
        views.ResendConfirmationView.as_view(),
        name="resend-confirmation",
    ),
    # Password reset endpoints
    path(
        "forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    # Profile endpoint
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # Token refresh endpoint
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Logout endpoint (deactivates FCM devices)
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # ========== ADMIN ENDPOINTS (User Management) ==========
    # Users
    path(
        "admin/users/",
        admin_views.UserListCreateView.as_view(),
        name="admin-users-list",
    ),
    path(
        "admin/users/search/",
        admin_views.UserSearchView.as_view(),
        name="admin-users-search",
    ),
    path(
        "admin/users/<int:user_id>/",
        admin_views.UserDetailView.as_view(),
        name="admin-users-detail",
    ),
    path(
        "admin/users/<int:user_id>/status/",
        admin_views.UserStatusView.as_view(),
        name="admin-users-status",
    ),
    path(
        "admin/users/<int:user_id>/roles/",
        admin_views.UserRolesView.as_view(),
        name="admin-users-roles",
    ),
    # Roles
    path("admin/roles/", admin_views.RoleListView.as_view(), name="admin-roles-list"),
]
