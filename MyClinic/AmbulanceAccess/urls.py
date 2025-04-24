from django.urls import path
from .views import AmbulanceView,ToggleAmbulanceStatusView,AmbulanceByUserView,AmbulanceStatusFilterView, AmbulanceDeleteView

urlpatterns = [
    path('register/', AmbulanceView.as_view(), name='ambulance_register'),
    path('toggle/<str:ambulance_id>/<str:vehicle_number>/',
          ToggleAmbulanceStatusView.as_view(), name='toggle-ambulance-status'),
    path('count/<str:ambulance_id>/', AmbulanceByUserView.as_view(), name='ambulance-count-active-or-inactive'),
    path('status/', AmbulanceStatusFilterView.as_view(), name='ambulance-status-filter'),
     path('delete/<str:ambulance_id>/<str:vehicle_number>/', AmbulanceDeleteView.as_view(), name='delete-ambulance'),
]
