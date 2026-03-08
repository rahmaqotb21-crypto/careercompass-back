from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ForgotPasswordView, ResetPasswordView, GoogleCallbackView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:uid>/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
]
