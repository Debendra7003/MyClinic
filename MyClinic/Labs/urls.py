from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, LabReportViewSet, LabProfileViewSet, LabTypeViewSet, LabSearchViewSet, CentralSearchView, LabAvailabilityViewSet


router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet)
router.register(r'lab-reports', LabReportViewSet)
router.register(r'lab-profiles', LabProfileViewSet)
router.register(r'lab-types', LabTypeViewSet)
router.register(r'lab-search', LabSearchViewSet, basename='lab-search')
router.register(r'availability', LabAvailabilityViewSet, basename='lab-availability')

urlpatterns = [
    path('search/', CentralSearchView.as_view(), name='central-search'),
    path('', include(router.urls)),
]