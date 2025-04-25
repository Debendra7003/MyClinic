from rest_framework import serializers
from .models import PatientProfile, Prescription, Insurance
from DoctorAccess.models import DoctorAppointment

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id','user_id', 'date_of_birth','age','gender', 'address', 'created_at']
        read_only_fields = ['id','user_id', 'created_at']

class PrescriptionSerializer(serializers.ModelSerializer):
    patient_user_id = serializers.CharField(source='patient.user.user_id', read_only = True)
    class Meta:
        model = Prescription
        fields = ['id', 'file', 'description', 'uploaded_at', 'patient', 'patient_user_id']
        read_only_fields = ['id', 'uploaded_at']

class InsuranceSerializer(serializers.ModelSerializer):
    patient_user_id = serializers.CharField(source='user.user_id', read_only = True)
    class Meta:
        model = Insurance
        fields = ['id', 'provider', 'policy_number', 'created_at', 'patient_user_id']

class PatientAppointmentUpdateSerializer(serializers.ModelSerializer):
    date_of_visit = serializers.DateField(required=True)
    visit_time = serializers.TimeField(required=True)
    shift = serializers.CharField(required=True)

    class Meta:
        model = DoctorAppointment
        fields = ['date_of_visit', 'visit_time', 'shift']

# class AmbulanceRequestSerializer(serializers.ModelSerializer):
#     patient_user_id = serializers.CharField(source='patient.user.user_id', read_only = True)
#     class Meta:
#         model = AmbulanceRequest
#         fields = ['id', 'location', 'status', 'created_at', 'patient_user_id']