from django.urls import path
from .views import UserRegisterView, UserLoginView, GoogleSignInView, FirebaseTokenView, EmailOTPVerifyView, SMSOTPVerifyView, PasswordResetRequestOTPView, PasswordResetVerifyOTPView, PasswordResetConfirmOTPView, privacy_policy
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/',UserLoginView.as_view(), name='user-login'),
    path('firebase-token/', FirebaseTokenView.as_view(), name='firebase-token'),
    path('google-signin/', GoogleSignInView.as_view(), name='google-signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-email-otp/', EmailOTPVerifyView.as_view(), name='verify_email_otp'),
    path('verify-sms-otp/', SMSOTPVerifyView.as_view(), name='verify_sms_otp'),
    path('password-reset/request-otp/', PasswordResetRequestOTPView.as_view(), name='password_reset_request_otp'),
    path('password-reset/verify-otp/', PasswordResetVerifyOTPView.as_view(), name='password_reset_verify_otp'),
    path('password-reset/confirm-otp/', PasswordResetConfirmOTPView.as_view(), name='password_reset_confirm_otp'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    


]
