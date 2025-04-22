from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, LabReportViewSet, LabProfileViewSet, LabTypeViewSet

router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet)
router.register(r'lab-reports', LabReportViewSet)
router.register(r'lab-profiles', LabProfileViewSet)
router.register(r'lab-types', LabTypeViewSet)
urlpatterns = [
    path('', include(router.urls)),
]