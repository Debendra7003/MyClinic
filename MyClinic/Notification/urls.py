from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminNotificationViewSet, SecureNotificationImageView

router = DefaultRouter()
router.register(r'admin/notifications', AdminNotificationViewSet, basename='admin-notification')

urlpatterns = [
    path('secure-image/<str:filename>/', SecureNotificationImageView.as_view(), name='secure_notification_image'),
    path('', include(router.urls)),

]