from rest_framework import serializers
from .models import PatientProfile, Prescription, AmbulanceRequest
from Core.models import Insurance

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'date_of_birth', 'phone', 'address', 'created_at']

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'file', 'description', 'uploaded_at']

class AmbulanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbulanceRequest
        fields = ['id', 'location', 'status', 'created_at']

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['id', 'provider', 'policy_number', 'created_at']