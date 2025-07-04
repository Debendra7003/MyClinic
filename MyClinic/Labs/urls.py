from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( LabTestViewSet, LabReportViewSet, LabProfileViewSet, LabTypeViewSet, 
                    LabSearchViewSet, CentralSearchView, LabAvailabilityViewSet, SecureFileDownloadView )


router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet)
router.register(r'lab-reports', LabReportViewSet)
router.register(r'lab-profiles', LabProfileViewSet)
router.register(r'lab-types', LabTypeViewSet)
router.register(r'lab-search', LabSearchViewSet, basename='lab-search')
router.register(r'availability', LabAvailabilityViewSet, basename='lab-availability')

urlpatterns = [
    path('search/', CentralSearchView.as_view(), name='central-search'),
    path('secure-download/<str:filename>/', SecureFileDownloadView.as_view(), name='secure-file-download'),

    path('', include(router.urls)),
]