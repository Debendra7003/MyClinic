from rest_framework import serializers
from .models import Ambulance
from LoginAccess.models import User

class AmbulanceSerializer(serializers.ModelSerializer):
    ambulance_id = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ambulance
        fields = [
            'ambulance_id', 'user', 'service_name', 'vehicle_number',
            'phone_number', 'whatsapp_number', 'service_area', 'active'
        ]

    def get_user(self, obj):
        return obj.ambulance_id.user_id

    def create(self, validated_data):
        user_id_str = validated_data.pop('ambulance_id')
        try:
            user = User.objects.get(user_id=user_id_str)
        except User.DoesNotExist:
            raise serializers.ValidationError({'ambulance_id': 'User not found.'})
        validated_data['ambulance_id'] = user
        return Ambulance.objects.create(**validated_data)
