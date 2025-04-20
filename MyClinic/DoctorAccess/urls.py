from django.urls import path
from .views import DoctorRegistrationView

urlpatterns = [
    path('register/', DoctorRegistrationView.as_view(), name='doctor-register'),
]
