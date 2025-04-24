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
    
    def update(self, instance, validated_data):
        doctor_user_id = validated_data.pop('doctor', None)
        if doctor_user_id:
            try:
                user = User.objects.get(user_id=doctor_user_id)
                validated_data['doctor'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"doctor": "Doctor with this user_id does not exist."})
        return super().update(instance, validated_data)