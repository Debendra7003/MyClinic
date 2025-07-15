from django.urls import path, include
from .views import AdminCostingAnalyticsView, CostingConfigViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'costing-configs', CostingConfigViewSet, basename='costingconfig')
urlpatterns = [
    path('costing-analytics/', AdminCostingAnalyticsView.as_view(), name='admin_costing_analytics'),
    path('', include(router.urls)),
]