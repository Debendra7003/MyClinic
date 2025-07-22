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
        read_only_fields = ['id', 'uploaded_at','patient']

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

    def validate(self, data):
        instance = self.getattr(self, 'instance', None)
        doctor_id = instance.doctor_id if instance else None
        date_of_visit = data.get('date_of_visit')
        visit_time = data.get('visit_time')
        shift = data.get('shift')
        conflict = DoctorAppointment.objects.filter(
            doctor_id=doctor_id,
            date_of_visit=date_of_visit,
            shift=shift,
            visit_time=visit_time,
            cancelled=False
        )
        if instance:
            conflict = conflict.exclude(pk=instance.pk)
        if conflict.exists():
            raise serializers.ValidationError(
                {"visit_time": "This visit time is already booked for the selected shift and date."}
            )
        return data
        

# class AmbulanceRequestSerializer(serializers.ModelSerializer):
#     patient_user_id = serializers.CharField(source='patient.user.user_id', read_only = True)
#     class Meta:
#         model = AmbulanceRequest
#         fields = ['id', 'location', 'status', 'created_at', 'patient_user_id']