from django.urls import path
from . import views

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
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('refresh/', views.RefreshTokenView.as_view(), name='refresh'),
]
