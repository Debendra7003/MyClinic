from rest_framework import serializers
from .models import CostingConfig

class CostingConfigSerializer(serializers.ModelSerializer):
    entity_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CostingConfig
        fields = '__all__'
        read_only_fields = ['id']

    def get_entity_name(self, obj):
        if obj.entity:
            return f"{obj.entity.first_name} {obj.entity.last_name}".strip()
        return ""
