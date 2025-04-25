from django.db import models
import random
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
    

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    available = models.BooleanField(default=True)
    shift = models.CharField(
        max_length=50,
        choices=[
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
            ('evening', 'Evening'),
            ('night', 'Night')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'shift')

    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.shift})"



def generate_registration_number():
    return str(random.randint(1000000000, 9999999999))
class DoctorAppointment(models.Model):
    doctor_id = models.ForeignKey(User,on_delete= models.CASCADE, related_name='Doctor_id_appointment')
    doctor_name = models.CharField(max_length=100)
    specialist = models.CharField(max_length=100)
    patient_id = models.ForeignKey(User,on_delete= models.CASCADE, related_name='patient_id')
    patient_name = models.CharField(max_length=100)
    patient_number =  models.CharField(max_length=100)
    patient_age = models.CharField(max_length=20) 
    patient_gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    date_of_visit = models.DateField()
    shift = models.CharField(max_length=50,
        choices=[
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
            ('evening', 'Evening'),
            ('night', 'Night')])
    visit_time = models.TimeField()
    booked_at=models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    registration_number = models.CharField(max_length=10, unique=True, default=generate_registration_number, editable=False)

    def __str__(self):
        return f"{self.registration_number} - {self.doctor_name} -> {self.patient_name}"






     
