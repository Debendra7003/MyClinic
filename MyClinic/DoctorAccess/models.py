from django.db import models
import random
from LoginAccess.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
# Create your models here.
class DoctorRegistration(models.Model):
    doctor = models.ForeignKey(User,on_delete= models.CASCADE, related_name='Doctor_id')
    doctor_name = models.CharField(max_length=100)
    specialist = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique= True)
    clinic_name = models.CharField(max_length=100)
    clinic_address = models.CharField(max_length=100)
    experience = models.IntegerField()
    status = models.BooleanField(default=False)
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
    delay_minutes = models.IntegerField(default=0)
    booked_at=models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    registration_number = models.CharField(max_length=10, unique=True, default=generate_registration_number, editable=False)

    # def calculate_estimated_time(self):
    #     """
    #     Calculate the estimated time for the patient to see the doctor.
    #     """
    #     appointments = DoctorAppointment.objects.filter(
    #         doctor_id=self.doctor_id,
    #         date_of_visit=self.date_of_visit,
    #         shift=self.shift,
    #         cancelled=False
    #     ).order_by('visit_time')

    #     completed_appointments = appointments.filter(checked=True).count()
    #     # position_in_queue = list(appointments).index(self)
    #     position_in_queue = appointments.filter(visit_time__lt=self.visit_time).count()

    #     # Assuming each appointment takes 15 minutes on average
    #     estimated_time = (position_in_queue - completed_appointments) * 15 + self.delay_minutes
    #     return estimated_time
    

    def format_minutes(self, minutes):
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours} hr {mins} mins"
        elif hours > 0:
            return f"{hours} hr"
        else:
            return f"{mins} mins"
        
    def calculate_estimated_time(self):
        """
        Combines estimated queue-based waiting time with real-time appointment clock.
        Returns both estimated and actual (clock) wait times.
        """
        ist = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        appointment_time = datetime.combine(self.date_of_visit, self.visit_time)
        appointment_time = ist.localize(appointment_time)
        real_wait = (appointment_time - now).total_seconds() / 60 # minutes
        real_wait = max(0, int(real_wait))

        appointments = DoctorAppointment.objects.filter(
            doctor_id=self.doctor_id,
            date_of_visit=self.date_of_visit,
            shift=self.shift,
            cancelled=False
        ).order_by('visit_time')

        earlier_appointments = appointments.filter(visit_time__lt=self.visit_time)
        pending_before_me = earlier_appointments.filter(checked=False).count()

        estimated_wait = pending_before_me * 15 + self.delay_minutes

        return {
            "real_wait_minutes": real_wait,
            "real_wait_display": self.format_minutes(real_wait),
            "estimated_wait_minutes": estimated_wait,
            "estimated_wait_display": self.format_minutes(estimated_wait)
        }

    def __str__(self):
        return f"{self.registration_number} - {self.doctor_name} -> {self.patient_name}"






     
