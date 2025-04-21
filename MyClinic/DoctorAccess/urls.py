from django.urls import path
from .views import DoctorRegistrationView, DoctorProfileAPIView

urlpatterns = [
    path('register/', DoctorRegistrationView.as_view(), name='doctor-register'),
    path('get_all/', DoctorProfileAPIView.as_view(), name='get-all-doctors'),             # GET all
    path('get/<str:doctor_id>/', DoctorProfileAPIView.as_view(), name='doctor-detail')  # GET, PUT, DELETE
]
