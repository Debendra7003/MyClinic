from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PatientProfile, Prescription, AmbulanceRequest
from .serializers import (
    PatientProfileSerializer, PrescriptionSerializer,
    AmbulanceRequestSerializer, InsuranceSerializer
)
from Core.models import Insurance
# from django.contrib.auth.models import User

class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PatientProfile.objects.all()
        return PatientProfile.objects.filter(user=user)

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Prescription.objects.all()
        return Prescription.objects.filter(patient__user=user)

class AmbulanceRequestViewSet(viewsets.ModelViewSet):
    queryset = AmbulanceRequest.objects.all()
    serializer_class = AmbulanceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AmbulanceRequest.objects.all()
        return AmbulanceRequest.objects.filter(patient__user=user)

class InsuranceViewSet(viewsets.ModelViewSet):
    queryset = Insurance.objects.all()
    serializer_class = InsuranceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Insurance.objects.all()
        return Insurance.objects.filter(user=user)




















# from rest_framework import viewsets, permissions, status, generics
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from .models import (
#     PatientProfile, MedicalHistory, Allergy, Medication,
#     FamilyMedicalHistory, Document, PatientPreference
# )
# from .serializers import (
#     PatientProfileSerializer, MedicalHistorySerializer, AllergySerializer,
#     MedicationSerializer, FamilyMedicalHistorySerializer, DocumentSerializer,
#     PatientPreferenceSerializer, FullPatientProfileSerializer
# )

# class IsPatientOrAdmin(permissions.BasePermission):
#     """
#     Custom permission to allow only the patient or admin to access their profile
#     """
#     def has_object_permission(self, request, view, obj):
#         # Check if the user is the patient or an admin
#         return obj.user == request.user or request.user.is_staff

# class PatientProfileViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing patient profiles"""
    
#     queryset = PatientProfile.objects.all()
#     serializer_class = PatientProfileSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's profile"""
#         user = self.request.user
#         if user.is_staff:
#             return PatientProfile.objects.all()
#         return PatientProfile.objects.filter(user=user)
    
#     @action(detail=False, methods=['get'])
#     def me(self, request):
#         """Get the current user's profile"""
#         try:
#             profile = PatientProfile.objects.get(user=request.user)
#             serializer = FullPatientProfileSerializer(profile)
#             return Response(serializer.data)
#         except PatientProfile.DoesNotExist:
#             return Response(
#                 {"detail": "Patient profile not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

# class MedicalHistoryViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing medical history"""
    
#     queryset = MedicalHistory.objects.all()
#     serializer_class = MedicalHistorySerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's medical history"""
#         user = self.request.user
#         if user.is_staff:
#             return MedicalHistory.objects.all()
#         return MedicalHistory.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating a medical history record"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)

# class AllergyViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing allergies"""
    
#     queryset = Allergy.objects.all()
#     serializer_class = AllergySerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's allergies"""
#         user = self.request.user
#         if user.is_staff:
#             return Allergy.objects.all()
#         return Allergy.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating an allergy record"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)

# class MedicationViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing medications"""
    
#     queryset = Medication.objects.all()
#     serializer_class = MedicationSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's medications"""
#         user = self.request.user
#         if user.is_staff:
#             return Medication.objects.all()
#         return Medication.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating a medication record"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)

# class FamilyMedicalHistoryViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing family medical history"""
    
#     queryset = FamilyMedicalHistory.objects.all()
#     serializer_class = FamilyMedicalHistorySerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's family medical history"""
#         user = self.request.user
#         if user.is_staff:
#             return FamilyMedicalHistory.objects.all()
#         return FamilyMedicalHistory.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating a family medical history record"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)

# class DocumentViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing medical documents"""
    
#     queryset = Document.objects.all()
#     serializer_class = DocumentSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's documents"""
#         user = self.request.user
#         if user.is_staff:
#             return Document.objects.all()
#         return Document.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating a document record"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)

# class PatientPreferenceViewSet(viewsets.ModelViewSet):
#     """ViewSet for managing patient preferences"""
    
#     queryset = PatientPreference.objects.all()
#     serializer_class = PatientPreferenceSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPatientOrAdmin]
    
#     def get_queryset(self):
#         """Filter queryset to return only the current user's preferences"""
#         user = self.request.user
#         if user.is_staff:
#             return PatientPreference.objects.all()
#         return PatientPreference.objects.filter(patient__user=user)
    
#     def perform_create(self, serializer):
#         """Automatically set the patient when creating preferences"""
#         patient = PatientProfile.objects.get(user=self.request.user)
#         serializer.save(patient=patient)