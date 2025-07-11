from rest_framework import viewsets
from MyClinic.permissions import IsAdmin, IsReadOnly
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from django.http import FileResponse, Http404
from django.conf import settings
import os
from MyClinic.utils import send_push_notification
from LoginAccess.models import User

class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsReadOnly| IsAdmin] 
#     # permission_classes = [IsAuthenticated & (IsReadOnly | IsAdmin)]

    def perform_create(self, serializer):
        notification = serializer.save()
        # Get all patients with a valid FCM token
        patients = User.objects.filter(role='patient', is_active=True).exclude(firebase_registration_token__isnull=True).exclude(firebase_registration_token='')
        for patient in patients:
            print({
                    "image": notification.image.url if notification.image else "",
                    "url": notification.url or "",
                    "tags": notification.tags,
                                    "image1":f"{os.getenv('BASE_URL')}/notification/secure-image/{os.path.basename(notification.image.name)}" if notification.image else None,

                })
            send_push_notification(
                registration_token=patient.firebase_registration_token,
                title=notification.title,
                body=notification.body,
                image=f"{os.getenv('BASE_URL')}/notification/secure-image/{os.path.basename(notification.image.name)}" if notification.image else None,
                data={
                    "image": notification.image.url if notification.image else "",
                    "url": notification.url or "",
                    "tags": notification.tags,
                }
            )


class SecureNotificationImageView(APIView):
    permission_classes = [IsReadOnly| IsAdmin]

    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, 'notifications/', filename)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
        raise Http404("Image not found")