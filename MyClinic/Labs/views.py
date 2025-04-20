from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LabTest, LabReport
from .serializers import LabTestSerializer, LabReportSerializer

class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LabTest.objects.all()
        return LabTest.objects.filter(patient__user=user)

class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LabReport.objects.all()
        return LabReport.objects.filter(lab_test__patient__user=user)