from rest_framework import serializers
from .models import CostingConfig
from django.db import models
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
    def validate(self, data):
        entity = data.get('entity') or (self.instance.entity if self.instance else None)
        entity_type = data.get('entity_type') or (self.instance.entity_type if self.instance else None)
        effective_from = data.get('effective_from') or (self.instance.effective_from if self.instance else None)
        effective_to = data.get('effective_to') or (self.instance.effective_to if self.instance else None)

        instance_id = self.instance.id if self.instance else None

        # Handle open-ended new config (effective_to=None means it's ongoing)
        if not effective_to:
            # Check if it overlaps with any ongoing or future config
            overlapping = CostingConfig.objects.filter(
                entity=entity,
                entity_type=entity_type
            ).exclude(
                id=instance_id
            ).filter(
                models.Q(effective_to__isnull=True) |  # Ongoing
                models.Q(effective_to__gte=effective_from)
            )
        else:
            # Closed period: Check overlap with other configs
            overlapping = CostingConfig.objects.filter(
                entity=entity,
                entity_type=entity_type
            ).exclude(
                id=instance_id
            ).filter(
                models.Q(effective_to__isnull=True, effective_from__lte=effective_to) |
                models.Q(effective_to__gte=effective_from, effective_from__lte=effective_to)
            )

        if overlapping.exists():
            raise serializers.ValidationError("Overlapping costing configuration exists for this entity and period.")

        return data
