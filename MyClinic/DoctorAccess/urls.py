from django.urls import path, include
from .views import (DoctorRegistrationView, DoctorProfileAPIView, DoctorSpecialist,DoctorAppointmentView, 
GetAppointment, DoctorAvailabilityViewSet, AppointmentChecked, NotifyShiftDelay)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'availability', DoctorAvailabilityViewSet, basename='doctor-availability')

urlpatterns = [
    path('register/', DoctorRegistrationView.as_view(), name='doctor-register'),
    path('get_all/', DoctorProfileAPIView.as_view(), name='get-all-doctors'),             # GET all
    path('get/<str:doctor_id>/', DoctorProfileAPIView.as_view(), name='doctor-detail'),  # GET, PUT, DELETE
    path('specialist/<str:specialist>/', DoctorSpecialist.as_view(), name ='doctor-by-specialisation'),
    path('appointment/', DoctorAppointmentView.as_view(), name='doctor-appointment'),
    path('appointmentlist/<str:lookup_value>/',GetAppointment.as_view(), name='get-appointment-list'),
    path('appointmentlist/',GetAppointment.as_view(), name='get-all-appointment-list'),
    path('appointment-checked/<str:registration_number>/',AppointmentChecked.as_view(), name='doctor-appointment-checked'),
    path('notify-shift-delay/', NotifyShiftDelay.as_view(), name='notify-shift-delay'),
    path('', include(router.urls))


]
