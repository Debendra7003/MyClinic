from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DoctorRegistrationSerializer,DoctorAppointmentSerializer, DoctorAvailabilitySerializer, AppointmentCheckedSerializer
from .models import DoctorRegistration, DoctorAppointment, DoctorAvailability
from LoginAccess.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from MyClinic.permissions import IsDoctor, IsPatient, IsReadOnly
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

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
    # permission_classes = [IsDoctor]
    permission_classes = [IsAuthenticated]

    def get(self, request, lookup_value=None):
        # Try matching against doctor_id, patient_id, or registration_number
        if lookup_value:
            try:
                date_value = datetime.strptime(lookup_value, "%Y-%m-%d").date()
                appointments = DoctorAppointment.objects.filter(date_of_visit=date_value)
            except ValueError:
                appointments = DoctorAppointment.objects.filter(
                    Q(doctor_id__user_id=lookup_value) |
                    Q(patient_id__user_id=lookup_value) |
                    Q(registration_number=lookup_value)
                )

            if not appointments.exists():
                return Response(
                    {"message": f"No appointments found for value '{lookup_value}'"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            appointments = DoctorAppointment.objects.all()

        serializer = DoctorAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




#---------------------------------------------- Doctor Appointment Check functionality-------------------------------------------------------------------


class AppointmentChecked(APIView):
    permission_classes = [IsDoctor]

    def patch(self, request, registration_number):
        try:
            doctor = DoctorAppointment.objects.get(registration_number=registration_number)
        except DoctorAppointment.DoesNotExist:
            return Response({"error": "Appointment with the given registration number not found."}, status=status.HTTP_404_NOT_FOUND)

        if 'checked' not in request.data:
            return Response({"error": "'checked' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppointmentCheckedSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Checked field updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#--------------------------------------------- Doctor Availability Date Shift functionality------------------------------------------------------------------------

class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor | IsPatient]

    def get_queryset(self):
        if self.request.user.role == 'patient':
            return DoctorAvailability.objects.all()
        elif self.request.user.role == 'doctor':
            return DoctorAvailability.objects.filter(doctor=self.request.user)
        return DoctorAvailability.objects.none()
    
    def perform_create(self, serializer):
        try:
            if self.request.user.role != 'doctor':
                raise ValidationError({
                    "error": "Only doctors are allowed to create availability."
                })
            serializer.save(doctor=self.request.user)

        except IntegrityError:
            raise ValidationError({
                "error": "This availability already exists for the selected date, shift and time."
            })
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.role == 'lab':
            raise serializers.ValidationError("You are not authorized to update.")
        elif user.role == 'patient':
            raise serializers.ValidationError("You are not authorized to update.")

        # Perform the update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.role != 'doctor':
            raise serializers.ValidationError("You are not authorized to delete this availability.")

        self.perform_destroy(instance)
        return Response({"message": "Availability deleted successfully."}, status=status.HTTP_200_OK)
