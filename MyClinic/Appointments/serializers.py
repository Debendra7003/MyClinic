from rest_framework import serializers
from .models import Appointment
from Patients.serializers import PatientProfileSerializer
from Core.models import Clinic

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'address', 'phone']

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'clinic', 'doctor', 'start_time', 'end_time', 'status', 'created_at', 'updated_at']