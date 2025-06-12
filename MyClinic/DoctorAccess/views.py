from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DoctorRegistrationSerializer,DoctorAppointmentSerializer, DoctorAvailabilitySerializer, AppointmentCheckedSerializer, AppointmentCancelledSerializer
from .models import DoctorRegistration, DoctorAppointment, DoctorAvailability
from LoginAccess.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from MyClinic.permissions import IsDoctor, IsPatient, IsReadOnly, IsAdmin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from MyClinic.utils import send_push_notification, send_scheduled_push_notification
from .tasks import send_appointment_reminder

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
    permission_classes = [IsAuthenticated]
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
    permission_classes =[IsAuthenticated]
    def get(self, request, specialist):
        doctor = DoctorRegistration.objects.filter(specialist = specialist)
        if doctor.exists():
            serializer = DoctorRegistrationSerializer(doctor, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response ({"message": f"No doctors avialable with specialist '{specialist}'"}, status=status.HTTP_404_NOT_FOUND)
    
class DoctorAppointmentView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        serializer = DoctorAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                appointment = serializer.save()
                # Push Notification to doctor when an appointment is booked
                doctor = appointment.doctor_id
                if doctor.firebase_registration_token:
                    send_push_notification(
                        registration_token=doctor.firebase_registration_token,
                        title="New Appointment Booked",
                        body=f"An appointment has been booked by {appointment.patient_name} on {appointment.date_of_visit} at {appointment.visit_time}.",
                    )

                # Schedule a notification for the patient a day before the appointment
                patient = appointment.patient_id
                if patient.firebase_registration_token:
                    scheduled_time = datetime.combine(appointment.date_of_visit, appointment.visit_time) - timedelta(days=1)
                    send_appointment_reminder.apply_async(
                        args=[
                            patient.firebase_registration_token,
                            "Appointment Reminder",
                            "Your appointment with Dr. {appointment.doctor_name} is scheduled tomorrow at {appointment.visit_time}.",
                            None
                        ],
                        eta=scheduled_time
                    )
                    # send_scheduled_push_notification(
                    #     registration_token=patient.firebase_registration_token,
                    #     title="Appointment Reminder",
                    #     body=f"Your appointment with Dr. {appointment.doctor_name} is scheduled tomorrow at {appointment.visit_time}.",
                    #     delivery_time=appointment.date_of_visit - timedelta(days=1),
                    # )

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
            if doctor.patient_id.firebase_registration_token:
                send_push_notification(
                    registration_token=doctor.patient_id.firebase_registration_token,
                    title="Appointment Completed",
                    body=f"Your appointment with Dr. {doctor.doctor_name} has been completed.",
                )

            # # Notify all patients booked on the same day
            same_day_appointments = DoctorAppointment.objects.filter(
                doctor_id=doctor.doctor_id,
                date_of_visit=doctor.date_of_visit,
                shift=doctor.shift,
                cancelled=False
            ).order_by('visit_time')
            print(same_day_appointments)
            for appt in same_day_appointments:
                print(appt)
                if appt.checked:
                    continue  # Skip already completed appointments
                print("Here It is!!")
                # if appt.registration_number == registration_number:
                    # Notify the patient whose appointment is being marked as completed
                    # if appt.patient_id.firebase_registration_token:
                    #     send_push_notification(
                    #         registration_token=appt.patient_id.firebase_registration_token,
                    #         title="Appointment Completed",
                    #         body=f"Your appointment with Dr. {appt.doctor_name} has been completed.",
                    #     )
                    # break  # Stop notifying further once the current appointment is completed
                print("Also Here It is!!")
                # Notify other patients about the progress
                if appt.patient_id.firebase_registration_token:
                    combined_wait = appt.calculate_estimated_time()
                    real_wait = combined_wait["real_wait_minutes"]
                    estimated_wait = combined_wait["estimated_wait_minutes"]
                    real_wait_display = combined_wait["real_wait_display"]
                    estimated_wait_display = combined_wait["estimated_wait_display"]
                    final_wait = max(real_wait, estimated_wait)
                    final_wait_display = combined_wait["real_wait_display"] if real_wait >= estimated_wait else combined_wait["estimated_wait_display"]

                    if final_wait <= 0:
                        body = "You are next. Please be ready."
                    elif final_wait <= 10:
                        body = f"Get ready! Your appointment is in approximately {final_wait_display}."
                    else:
                        body = f"Your appointment is estimated in {final_wait_display}. We will keep you updated."
                    print("Estimated_time:",estimated_wait, "Real_wait:",real_wait, "Final_wait:",final_wait, "Final_wait_display:",final_wait_display, "Real_wait_display:",real_wait_display, "Estimated_wait_display:",estimated_wait_display)
                    print("Message body:", body)
                    send_push_notification(
                            registration_token=appt.patient_id.firebase_registration_token,
                            title="Appointment Update",
                            body=body)
                    

                    # if estimated_time==0:
                    #     send_push_notification(
                    #     registration_token=appt.patient_id.firebase_registration_token,
                    #     title="Appointment Progress",
                    #     # body=f"Appointment {appt.registration_number} has been completed. Your turn is approaching.",
                    #      body=(
                    #             f"Appointment {appt.registration_number} has been completed. "
                    #             f"Your turn is next."),
                    # )
                    # elif estimated_time<0:
                    #     send_push_notification(
                    #     registration_token=appt.patient_id.firebase_registration_token,
                    #     title="Appointment Progress",
                    #     # body=f"Appointment {appt.registration_number} has been completed. Your turn is approaching.",
                    #      body=(
                    #             f"Appointment {appt.registration_number} has been completed. "
                    #             f"Your Waiting Time: {estimated_time} minutes."),
                    # )
                    # else:
                    #     send_push_notification(
                    #     registration_token=appt.patient_id.firebase_registration_token,
                    #     title="Appointment Progress",
                    #     # body=f"Appointment {appt.registration_number} has been completed. Your turn is approaching.",
                    #      body=(
                    #             f"Appointment {appt.registration_number} has been completed. "
                    #             f"Your turn is in next {estimated_time} minutes."),
                    # )

            return Response({"message": "Checked field updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)



        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppointmentCancelled(APIView):
    permission_classes = [IsDoctor | IsPatient]

    def patch(self, request, registration_number):
        try:
            doctor = DoctorAppointment.objects.get(registration_number=registration_number)
        except DoctorAppointment.DoesNotExist:
            return Response({"error": "Appointment with the given registration number not found."}, status=status.HTTP_404_NOT_FOUND)

        if 'cancelled' not in request.data:
            return Response({"error": "'cancelled' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppointmentCancelledSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cancelled field updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)



        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#--------------------------------------------- Doctor Availability Date Shift functionality------------------------------------------------------------------------

class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor | IsPatient | IsAdmin]

    def get_queryset(self):
        if self.request.user.role == 'patient' or self.request.user.is_admin:
            return DoctorAvailability.objects.all()
        elif self.request.user.role == 'doctor':
            return DoctorAvailability.objects.filter(doctor=self.request.user)
        return DoctorAvailability.objects.none()
    
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)
        # Check if data is a list (bulk) or dict (single)
        is_many = isinstance(data, list)
        if is_many:
            for item in data:
                item['doctor'] = self.request.user.user_id  # Set doctor for each item
            serializer = self.get_serializer(data=data, many=True)
        else:
            data['doctor'] = self.request.user.user_id
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        # Bulk create if many, else normal save
        if isinstance(serializer.validated_data, list):
            doctor_instance = self.request.user  # This is the User instance
            DoctorAvailability.objects.bulk_create([
                        DoctorAvailability(
                        doctor=doctor_instance,
                        **{k: v for k, v in item.items() if k != 'doctor'}
                        ) for item in serializer.validated_data])
        else:
            serializer.save(doctor=self.request.user)

    # def perform_create(self, serializer):
    #     try:
    #         if self.request.user.role != 'doctor':
    #             raise ValidationError({
    #                 "error": "Only doctors are allowed to create availability."
    #             })
    #         serializer.save(doctor=self.request.user)

    #     except IntegrityError:
    #         raise ValidationError({
    #             "error": "This availability already exists for the selected date, shift and time."
    #         })
        
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


class NotifyShiftDelay(APIView):
    permission_classes = [IsDoctor]

    def post(self, request):
        try:
            doctor = request.user
            shift = request.data.get('shift')
            date_of_visit = request.data.get('date_of_visit')
            delay_minutes = int(request.data.get('delay_minutes', 0))

            if not shift or not date_of_visit:
                return Response({"error": "Shift and date_of_visit are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Update delay_minutes for all appointments in the shift
            appointments = DoctorAppointment.objects.filter(
                doctor_id=doctor,
                date_of_visit=date_of_visit,
                shift=shift,
                cancelled=False
            )
            appointments.update(delay_minutes=delay_minutes)

            # Notify all patients in the shift
            for appointment in appointments:
                if appointment.patient_id.firebase_registration_token:
                    send_push_notification(
                        registration_token=appointment.patient_id.firebase_registration_token,
                        title="Appointment Delay Notification",
                        body=f"Your appointment with Dr. {doctor.doctor_name} will be delayed by {delay_minutes} minutes.",
                    )

            return Response({"message": "Patients notified about the delay."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)