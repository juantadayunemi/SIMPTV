from django.urls import path
from . import views

app_name = "auth_app"

urlpatterns = [
    # Auth endpoints
    path("login/", views.LoginView.as_view(), name="login"),
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    # path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
]
