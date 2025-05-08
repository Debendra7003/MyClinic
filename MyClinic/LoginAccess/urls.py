from django.urls import path
from .views import UserRegisterView, UserLoginView, GoogleSignInView, FirebaseTokenView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/',UserLoginView.as_view(), name='user-login'),
    path('firebase-token/', FirebaseTokenView.as_view(), name='firebase-token'),
    path('google-signin/', GoogleSignInView.as_view(), name='google-signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

]
