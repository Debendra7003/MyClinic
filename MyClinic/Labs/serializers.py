from rest_framework import serializers
from .models import LabTest, LabReport
from Patients.serializers import PatientProfileSerializer

class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = ['id', 'file', 'description', 'published_at']

class LabTestSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(read_only=True)
    reports = LabReportSerializer(many=True, read_only=True)

    class Meta:
        model = LabTest
        fields = ['id', 'patient', 'test_type', 'scheduled_date', 'status', 'created_at', 'reports']