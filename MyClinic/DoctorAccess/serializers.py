from rest_framework import serializers
from .models import DoctorRegistration,DoctorAppointment
from LoginAccess.models import User


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    doctor = serializers.CharField(write_only=True)  # accepts "XOP7"
    doctor_user_id = serializers.SerializerMethodField(read_only=True)  # returns it back in response

    class Meta:
        model = DoctorRegistration
        fields = [
            'doctor', 'doctor_user_id', 'doctor_name', 'specialist', 'license_number',
            'clinic_name', 'clinic_address', 'experience', 'status', 'profile_image'
        ]

    def get_doctor_user_id(self, obj):
        return obj.doctor.user_id

    def create(self, validated_data):
        doctor_user_id = validated_data.pop('doctor')
        try:
            user = User.objects.get(user_id=doctor_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"doctor": "Doctor with this user_id does not exist."})
        validated_data['doctor'] = user
        return DoctorRegistration.objects.create(**validated_data)
    



class DoctorAppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.CharField(write_only=True)
    patient_id = serializers.CharField(write_only=True)
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    registration_number = serializers.CharField(read_only=True)

    class Meta:
        model = DoctorAppointment
        fields = ['registration_number',
            'doctor_id', 'doctor', 'doctor_name', 'specialist',
            'patient_id', 'patient', 'patient_name', 'patient_number',
            'patient_age', 'patient_gender',
            'date_of_visit', 'shift', 'visit_time'
        ]

    def get_doctor(self, obj):
        return obj.doctor_id.user_id

    def get_patient(self, obj):
        return obj.patient_id.user_id

    def create(self, validated_data):
        doctor_user_id = validated_data.pop('doctor_id')
        patient_user_id = validated_data.pop('patient_id')

        try:
            doctor = User.objects.get(user_id=doctor_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Invalid doctor ID'})

        try:
            patient = User.objects.get(user_id=patient_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'patient_id': 'Invalid patient ID'})

        validated_data['doctor_id'] = doctor
        validated_data['patient_id'] = patient

        return DoctorAppointment.objects.create(**validated_data)