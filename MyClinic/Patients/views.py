from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PatientProfile, Prescription, Insurance
from .serializers import (
    PatientProfileSerializer, PrescriptionSerializer,
    InsuranceSerializer, PatientAppointmentUpdateSerializer
)
from rest_framework import serializers
from MyClinic.permissions import IsPatient, IsReadOnly, IsDoctor, IsLab
from DoctorAccess.models import DoctorAppointment
from DoctorAccess.serializers import DoctorAppointmentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
    permission_classes = [IsPatient | IsDoctor | IsLab] 

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


class PatientAppointmentsView(APIView):
    permission_classes = [IsPatient]

    def get(self, request):
        try:
            patient_profile = PatientProfile.objects.get(user=request.user)
            appointments = DoctorAppointment.objects.filter(patient_id=request.user)
            serializer = DoctorAppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

class PatientAppointmentUpdate(APIView):
    permission_classes = [IsPatient]

    def patch(self, request, registration_number):
        try:
            appointment = DoctorAppointment.objects.get(registration_number=registration_number)
        except DoctorAppointment.DoesNotExist:
            return Response({"error": "Appointment with the given registration number not found."}, status=status.HTTP_404_NOT_FOUND)

        if 'date_of_visit' not in request.data:
            return Response({"error": "'date_of_visit' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        elif 'visit_time' not in request.data:
            return Response({"error": "'visit_time' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        elif 'shift' not in request.data:
            return Response({"error": "'shift' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PatientAppointmentUpdateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Appointment rescheduled successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
