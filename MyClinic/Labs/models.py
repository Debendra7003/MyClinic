import uuid
from django.db import models
from Patients.models import PatientProfile

class LabTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='lab_tests')
    test_type = models.CharField(max_length=255)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ], default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_type} for {self.patient.user.username}"

class LabReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='reports')
    file = models.TextField()
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.lab_test.test_type}"