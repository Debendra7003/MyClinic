import uuid
from django.db import models
from Patients.models import PatientProfile
from django.contrib.auth import get_user_model
import random

User = get_user_model()
def generate_registration_number():
    return str(random.randint(1000000000, 9999999999))

class LabProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_profile')
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    home_sample_collection = models.BooleanField(default=False)
    # lab_types = models.ManyToManyField('LabType', related_name='labs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LabType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_profile = models.ForeignKey(LabProfile, on_delete=models.CASCADE, related_name='lab_types')
    name = models.CharField(max_length=255, unique=True)
    tests = models.JSONField(default=list)


    # def save(self, *args, **kwargs):
    #     self.name = self.name.lower()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# class TestType(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     lab_type = models.ForeignKey(LabType, on_delete=models.CASCADE, related_name='test_types')
#     name = models.CharField(max_length=255)
#     labs = models.ManyToManyField('LabProfile', related_name='test_types')

#     def __str__(self):
#         return f"{self.name} ({self.lab_type.name})"
    

class LabTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='lab_tests')
    lab_profile = models.ForeignKey(LabProfile, on_delete=models.CASCADE, related_name='lab_tests')
    test_type = models.CharField(max_length=255)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ('SCHEDULED', 'Scheduled'),
        ('RESCHEDULED', 'Rescheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ], default='SCHEDULED')
    registration_number = models.CharField(max_length=10, unique=True, default=generate_registration_number, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_type} for {self.patient.user}"

class LabReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='reports')
    file = models.TextField()
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.lab_test.test_type}"