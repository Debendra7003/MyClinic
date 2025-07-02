from django.urls import path
from .views import ( UserRegisterView, UserLoginView, GoogleSignInView, FirebaseTokenView, 
                    EmailOTPVerifyView, SMSOTPVerifyView, PasswordResetRequestOTPView, 
                    PasswordResetVerifyOTPView, PasswordResetConfirmOTPView, privacy_policy,
                     AdminAddUserView, AdminToggleActiveView, AdminDeleteUserView, AdminListUsersByRoleView )

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
    path('admin/add-user/', AdminAddUserView.as_view(), name='admin_add_user'),
    path('admin/user/<str:pk>/toggle-active/', AdminToggleActiveView.as_view(), name='admin_toggle_active'),
    path('admin/user/<str:pk>/delete/', AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('admin/list-users/', AdminListUsersByRoleView.as_view(), name='admin_list_users_by_role'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    


]
