from django.db import models
from LoginAccess.models import User

# Create your models here.
class Ambulance(models.Model):
    ambulance_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ambulance_id')
    service_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20,unique=True,null=False, blank=False)
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    service_area= models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    register_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.service_name} ({self.ambulance_id})"