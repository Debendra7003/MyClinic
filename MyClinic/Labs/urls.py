from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, LabReportViewSet, LabProfileViewSet, LabTypeViewSet, LabSearchViewSet


router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet)
router.register(r'lab-reports', LabReportViewSet)
router.register(r'lab-profiles', LabProfileViewSet)
router.register(r'lab-types', LabTypeViewSet)
router.register(r'lab-search', LabSearchViewSet, basename='lab-search')

urlpatterns = [
    path('', include(router.urls)),
]