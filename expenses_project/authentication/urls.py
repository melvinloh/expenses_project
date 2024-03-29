from django.urls import path
from .views import RegistrationView, LoginView, UsernameValidationView, EmailValidationView, UserActivationView, PasswordValidationView, LogoutView, ForgotPassword, ResetPassword
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"), 
    path('login', LoginView.as_view(), name="login"), 
    path('logout', LogoutView.as_view(), name="logout"), 
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate-username"), 
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"), 
    path('validate-password', csrf_exempt(PasswordValidationView.as_view()), name="validate-password"), 
    path('activate-user/<uidb64>/<token>/', UserActivationView.as_view(), name="activate-user"), 
    path('forgot-password', ForgotPassword.as_view(), name="forgot-password"), 
    path('reset-password/<uidb64>/<token>/', ResetPassword.as_view(), name="reset-password"), 
]