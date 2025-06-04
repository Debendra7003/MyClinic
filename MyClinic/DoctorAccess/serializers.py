from rest_framework import serializers
from .models import DoctorRegistration,DoctorAppointment, DoctorAvailability
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
        read_only_fields = ['status']
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
    
    def update(self, instance, validated_data):
        doctor_user_id = validated_data.pop('doctor', None)
        if doctor_user_id:
            try:
                user = User.objects.get(user_id=doctor_user_id)
                validated_data['doctor'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"doctor": "Doctor with this user_id does not exist."})
        return super().update(instance, validated_data)
    
# class DoctorAppointmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DoctorAppointment
#         fields = [
#             'id', 'doctor_id', 'doctor_name', 'specialist', 'patient_id',
#             'patient_name', 'patient_number', 'patient_age', 'patient_gender',
#             'date_of_visit', 'shift', 'visit_time', 'booked_at', 'registration_number', 'checked', 'cancelled'
#         ]
#         read_only_fields = ['id', 'booked_at', 'registration_number']

class AppointmentCheckedSerializer(serializers.ModelSerializer):
    checked = serializers.BooleanField(required=True)

    class Meta:
        model = DoctorAppointment
        fields = ['checked']
class AppointmentCancelledSerializer(serializers.ModelSerializer):
    cancelled = serializers.BooleanField(required=True)

    class Meta:
        model = DoctorAppointment
        fields = ['cancelled']

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    estimated_time = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAppointment
        fields = [
            'id', 'doctor_id', 'doctor_name', 'specialist', 'patient_id',
            'patient_name', 'patient_number', 'patient_age', 'patient_gender',
            'date_of_visit', 'shift', 'visit_time', 'booked_at', 'registration_number',
            'checked', 'cancelled', 'delay_minutes', 'estimated_time'
        ]
        read_only_fields = ['id', 'booked_at', 'registration_number', 'estimated_time']

    def validate(self, data):
        doctor_id = data.get('doctor_id')
        date_of_visit = data.get('date_of_visit')
        shift = data.get('shift')
        visit_time = data.get('visit_time')

        if DoctorAppointment.objects.filter(
            doctor_id=doctor_id,
            date_of_visit=date_of_visit,
            shift=shift,
            visit_time=visit_time,
            cancelled=False
        ).exists():
            raise serializers.ValidationError(
                {"visit_time": "This visit time is already booked for the selected shift and date."}
            )

        return data
    
    def get_estimated_time(self, obj):
        return obj.calculate_estimated_time()
    
class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = ['id', 'doctor', 'date','start_time','end_time','available', 'shift', 'created_at']
        read_only_fields = ['id', 'created_at','doctor']
