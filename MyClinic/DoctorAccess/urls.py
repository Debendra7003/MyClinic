from django.urls import path
from .views import DoctorRegistrationView, DoctorProfileAPIView, DoctorSpecialist,DoctorAppointmentView, GetAppointment

urlpatterns = [
    path('register/', DoctorRegistrationView.as_view(), name='doctor-register'),
    path('get_all/', DoctorProfileAPIView.as_view(), name='get-all-doctors'),             # GET all
    path('get/<str:doctor_id>/', DoctorProfileAPIView.as_view(), name='doctor-detail'),  # GET, PUT, DELETE
    path('specialist/<str:specialist>/', DoctorSpecialist.as_view(), name ='doctor-by-specialisation'),
    path('appointment/', DoctorAppointmentView.as_view(), name='doctor-appointment'),
    path('appointmentlist/<str:lookup_value>/',GetAppointment.as_view(), name='get-appointment-list'),
    path('appointmentlist/',GetAppointment.as_view(), name='get-all-appointment-list'),

]
