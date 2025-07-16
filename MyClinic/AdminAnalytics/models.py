from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CostingConfig(models.Model):
    ENTITY_TYPE_CHOICES = [
        ('doctor', 'Doctor'),
        ('lab', 'Lab'),
    ]
    COSTING_TYPE_CHOICES = [
        ('per_patient', 'Commission Per Patient'),
        ('fixed', 'Fixed Amount Commission'),
    ]
    entity_type = models.CharField(max_length=10, choices=ENTITY_TYPE_CHOICES)
    entity = models.ForeignKey(User, on_delete=models.CASCADE)
    costing_type = models.CharField(max_length=20, choices=COSTING_TYPE_CHOICES)
    per_patient_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    period = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('weekly', 'Weekly'),('yearly','Yearly')], blank=True, null=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('entity_type', 'entity', 'effective_from')

    def __str__(self):
        return f"{self.entity} ({self.entity_type}) - {self.costing_type}"