from django.db import models
from LoginAccess.models import User

# Create your models here.
class DoctorRegistration(models.Model):
    doctor = models.ForeignKey(User,on_delete= models.CASCADE, related_name='Doctor_id')
    doctor_name = models.CharField(max_length=100)
    specialist = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique= True)
    clinic_name = models.CharField(max_length=100)
    clinic_address = models.CharField(max_length=100)
    experience = models.IntegerField()
    status = models.CharField(max_length=10)
    profile_image = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.doctor_name} ({self.user_id})"