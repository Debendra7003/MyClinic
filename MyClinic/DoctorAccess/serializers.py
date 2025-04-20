from rest_framework import serializers
from .models import DoctorRegistration
from LoginAccess.models import User


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorRegistration
        fields = ['user_id', 'user', 'doctor_name', 'specialist', 'license_number',
                  'clinic_name', 'clinic_address', 'experience', 'profile_image']

    def get_user(self, obj):
        return obj.user_id.user_id  # return the string 'XOP7'

    def create(self, validated_data):
        user_id_str = validated_data.pop('user_id')

        try:
            user = User.objects.get(user_id=user_id_str)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Invalid user_id: user not found'})

        validated_data['user_id'] = user  # 🔁 use actual User instance
        return DoctorRegistration.objects.create(**validated_data)