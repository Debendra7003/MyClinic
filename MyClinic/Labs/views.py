from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LabTest, LabReport, LabProfile, LabType
from .serializers import LabTestSerializer, LabReportSerializer, LabProfileSerializer, LabTypeSerializer
from Patients.models import PatientProfile
from rest_framework import serializers
from rest_framework.permissions import BasePermission
from MyClinic.permissions import IsLab, IsPatient, IsReadOnly

class LabProfileViewSet(viewsets.ModelViewSet):
    queryset = LabProfile.objects.all()
    serializer_class = LabProfileSerializer
    permission_classes = [IsAuthenticated] # Labs can modify, others can view
    
    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only users with the 'lab' role can create a lab profile.")
        if LabProfile.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("A LabProfile already exists for this user.")
        serializer.save(user=self.request.user)
    # def perform_create(self, serializer):
        # if LabProfile.objects.filter(user=self.request.user).exists():
        #     raise serializers.ValidationError("A LabProfile already exists for this user.")
        # serializer.save(user=self.request.user)


class LabTypeViewSet(viewsets.ModelViewSet):
    queryset = LabType.objects.all()
    serializer_class = LabTypeSerializer
    permission_classes = [IsLab | IsReadOnly]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'lab_profile'):
            raise serializers.ValidationError("Only labs can create lab types.")
        serializer.save(lab_profile=self.request.user.lab_profile)

class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsPatient | IsLab] # Patients can book, labs can view/manage

    def get_queryset(self):
        user = self.request.user
        if user.role == 'lab':
            return LabTest.objects.filter(patient__user_role="patient")
        elif user.role == 'patient':
            return LabTest.objects.filter(patient__user=user)
        return LabTest.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'patient':
            raise serializers.ValidationError("Only patients can book lab tests.")
        try:
            patient_profile = PatientProfile.objects.get(user=self.request.user)
            serializer.save(patient=patient_profile)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("No patient profile found for the current user.")
        

class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [IsLab | IsPatient]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'lab':
            return LabReport.objects.filter(lab_test__lab_profile__user=user)
        elif user.role == 'patient':
            return LabReport.objects.filter(lab_test__patient__user=user)
        return LabReport.objects.none()
    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only labs can upload reports.")
        try:
            lab_test = LabTest.objects.get(id=self.request.data['lab_test'])
            serializer.save(lab_test=lab_test)
        except LabTest.DoesNotExist:
            raise serializers.ValidationError("No lab test found with the provided ID.")