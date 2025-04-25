from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PatientProfile, Prescription, Insurance
from .serializers import (
    PatientProfileSerializer, PrescriptionSerializer,
    InsuranceSerializer
)
from rest_framework import serializers
from MyClinic.permissions import IsPatient, IsReadOnly, IsDoctor, IsLab
# from django.contrib.auth.models import User


class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsPatient | IsReadOnly]
    lookup_field = 'user_id'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PatientProfile.objects.all()
        return PatientProfile.objects.filter(user=user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsPatient | IsDoctor | IsLab] # change to patient, doctor, lab

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Prescription.objects.all()
        return Prescription.objects.filter(patient__user=user)
    def perform_create(self, serializer):
        
        try:
            patient_profile = PatientProfile.objects.get(user=self.request.user)
            serializer.save(patient=patient_profile)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("No patient profile found for the current user.")


class InsuranceViewSet(viewsets.ModelViewSet):
    queryset = Insurance.objects.all()
    serializer_class = InsuranceSerializer
    permission_classes = [IsAuthenticated]  # Change to IsPatient, IsDoctor

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Insurance.objects.all()
        return Insurance.objects.filter(user=user)
    def perform_create(self, serializer):
        try:
            patient_profile = PatientProfile.objects.get(user=self.request.user)
            print(patient_profile)
            serializer.save(user=patient_profile.user)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("No patient profile found for the current user.")



# class AmbulanceRequestViewSet(viewsets.ModelViewSet):
#     queryset = AmbulanceRequest.objects.all()
#     serializer_class = AmbulanceRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return AmbulanceRequest.objects.all()
#         return AmbulanceRequest.objects.filter(patient__user=user)
#     def perform_create(self, serializer):
#         try:
#             patient_profile = PatientProfile.objects.get(user=self.request.user)
#             serializer.save(patient=patient_profile)
#         except PatientProfile.DoesNotExist:
#             raise serializers.ValidationError("No patient profile found for the current user.")
