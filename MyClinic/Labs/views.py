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
    permission_classes = [IsLab] # Labs can modify, others can view
    
    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only labs can create a lab profile.")
        if LabProfile.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("A LabProfile already exists for this lab.")
        serializer.save(user=self.request.user)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.user)
        if instance.user != request.user:
            raise serializers.ValidationError("You are not authorized to update this lab profile.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        if instance.user != request.user:
            raise serializers.ValidationError("You are not authorized to delete this lab profile.")
        return super().destroy(request, *args, **kwargs)
    


class LabTypeViewSet(viewsets.ModelViewSet):
    queryset = LabType.objects.all()
    serializer_class = LabTypeSerializer
    permission_classes = [IsLab | IsReadOnly] # Labs can modify, others can view

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'lab_profile'):
            raise serializers.ValidationError("Only labs can create lab types.")
        serializer.save(lab_profile=self.request.user.lab_profile)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_profile.user != request.user or self.request.user.role != 'lab':
            raise serializers.ValidationError("You are not authorized to update this lab type.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_profile.user != request.user or self.request.user.role != 'lab':
            raise serializers.ValidationError("You are not authorized to delete this lab type.")
        return super().destroy(request, *args, **kwargs)

    
class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsPatient | IsLab] # Patients can book, labs can view/manage

    def get_queryset(self):
        user = self.request.user
        if user.role == 'lab':
            if hasattr(user, 'lab_profile'):
                return LabTest.objects.filter(lab_profile=user.lab_profile)
            return LabTest.objects.none()
            # return LabTest.objects.filter(patient__user__role="patient")
        elif user.role == 'patient':
            return LabTest.objects.filter(patient__user=user)
        return LabTest.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'patient':
            raise serializers.ValidationError("Only patients can book lab tests.")
        try:
            patient_profile = PatientProfile.objects.get(user=self.request.user)
            lab_profile = LabProfile.objects.get(id=self.request.data.get('lab_profile'))
            serializer.save(patient=patient_profile, lab_profile=lab_profile)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("No patient profile found for the current user.")
        except LabProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid lab profile ID.")
        

class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [IsLab | IsPatient]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'lab':
            if hasattr(user, 'lab_profile'):
                return LabReport.objects.filter(lab_test__lab_profile=user.lab_profile)

            return LabReport.objects.none()

            # return LabReport.objects.filter(lab_test__patient__user__role="patient")

        elif user.role == 'patient':
            return LabReport.objects.filter(lab_test__patient__user=user)
        return LabReport.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only labs can upload reports.")
        
        lab_test_id = self.request.data.get('lab_test')
        if not lab_test_id:
            raise serializers.ValidationError({"lab_test": "This field is required."})
        
        try:
            lab_test = LabTest.objects.get(id=lab_test_id)
            if lab_test.lab_profile != self.request.user.lab_profile:
                raise serializers.ValidationError("You are not authorized to upload a report for this lab test.")
            serializer.save(lab_test=lab_test)
        except LabTest.DoesNotExist:
            raise serializers.ValidationError("No lab test found with the provided ID.")
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_test.lab_profile != request.user.lab_profile:
            raise serializers.ValidationError("You are not authorized to update this lab report.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_test.lab_profile != request.user.lab_profile:
            raise serializers.ValidationError("You are not authorized to delete this lab report.")
        return super().destroy(request, *args, **kwargs)