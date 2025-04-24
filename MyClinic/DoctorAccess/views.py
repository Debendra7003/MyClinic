from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DoctorRegistrationSerializer,DoctorAppointmentSerializer
from .models import DoctorRegistration, DoctorAppointment
from LoginAccess.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q

# from rest_framework.permissions import IsAuthenticated


#------------------------------------------------- Doctor Register functionality-----------------------------------------------------------
class DoctorRegistrationView(APIView):
    permission_classes=[AllowAny]
    def post(self, request, format=None):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    "message": "Doctor registered successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({
                    "error": "Integrity error occurred (likely duplicate license number)",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorProfileAPIView(APIView):
    permission_classes = [AllowAny]
#------------------------------------------------- Doctor get-all or get by ID functionality----------------------------------------------------------------
    def get(self, request, doctor_id=None):
        if doctor_id:
            doctor_instance = get_object_or_404(User, user_id=doctor_id)
            try:
                profile = DoctorRegistration.objects.get(doctor=doctor_instance)
                serializer = DoctorRegistrationSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DoctorRegistration.DoesNotExist:
                return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            profiles = DoctorRegistration.objects.all()
            serializer = DoctorRegistrationSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
#------------------------------------------------- Doctor Update functionality------------------------------------------------------------------------
    def put(self, request, doctor_id): 
        user = get_object_or_404(User, user_id=doctor_id)
        try:
            profile = DoctorRegistration.objects.get(doctor=user)
        except DoctorRegistration.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)        
        serializer = DoctorRegistrationSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#------------------------------------------------- Doctor Delete functionality-------------------------------------------------------------------------
    def delete(self, request, doctor_id):
        user = get_object_or_404(User, user_id=doctor_id)
        try:
            profile = DoctorRegistration.objects.get(doctor=user)
            profile.delete()
            return Response({"message": "Doctor profile deleted successfully"}, status=status.HTTP_200_OK)
        except DoctorRegistration.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
                
#------------------------------------------------- Doctor get by Specialisation functionality----------------------------------------------------------------
class DoctorSpecialist(APIView):
    permission_classes =[AllowAny]
    def get(self, request, specialist):
        doctor = DoctorRegistration.objects.filter(specialist = specialist)
        if doctor.exists():
            serializer = DoctorRegistrationSerializer(doctor, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response ({"message": f"No doctors avialable with specialist '{specialist}'"}, status=status.HTTP_404_NOT_FOUND)
    
class DoctorAppointmentView(APIView):
    permission_classes=[AllowAny]
    def post(self, request, format=None):
        serializer = DoctorAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                appointment = serializer.save()
                return Response({
                    "message": "Appointment booked successfully",
                    "data": DoctorAppointmentSerializer(appointment).data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": "Integrity error", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAppointment(APIView):
    permission_classes=[AllowAny]
    def get(self, request, lookup_value=None):
        # Try matching against doctor_id, patient_id, or registration_number
        if lookup_value:
            appointments = DoctorAppointment.objects.filter(
                Q(doctor_id__user_id=lookup_value) |
                Q(patient_id__user_id=lookup_value) |
                Q(registration_number=lookup_value) |
                Q(date_of_visit=lookup_value))

            if not appointments.exists():
                return Response(
                    {"message": f"No appointments found for value '{lookup_value}'"},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            appointments = DoctorAppointment.objects.all()

        serializer = DoctorAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)