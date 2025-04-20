import uuid
from django.db import models
from django.contrib.auth.models import User

class PatientProfile(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    # phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='prescriptions')
    file = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.username}"

class AmbulanceRequest(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='ambulance_requests')
    location = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Pending'),
        ('DISPATCHED', 'Dispatched'),
        ('COMPLETED', 'Completed'),
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ambulance Request by {self.patient.user.username}"



















# from django.db import models
# from django.contrib.auth import get_user_model
# from django.core.validators import RegexValidator

# User = get_user_model()

# class PatientProfile(models.Model):
#     """Extended profile information for patients"""
    
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#     )
    
#     BLOOD_GROUP_CHOICES = (
#         ('A+', 'A+'),
#         ('A-', 'A-'),
#         ('B+', 'B+'),
#         ('B-', 'B-'),
#         ('O+', 'O+'),
#         ('O-', 'O-'),
#         ('AB+', 'AB+'),
#         ('AB-', 'AB-'),
#     )
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
#     blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     profile_photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     city = models.CharField(max_length=100, blank=True, null=True)
#     state = models.CharField(max_length=100, blank=True, null=True)
#     country = models.CharField(max_length=100, blank=True, null=True)
#     pincode = models.CharField(max_length=10, blank=True, null=True)
#     emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
#     emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.user.first_name} {self.user.last_name}'s Profile"

# class MedicalHistory(models.Model):
#     """Patient's medical history records"""
    
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_histories')
#     condition_name = models.CharField(max_length=200)
#     diagnosed_date = models.DateField(blank=True, null=True)
#     treatment_notes = models.TextField(blank=True, null=True)
#     is_ongoing = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s {self.condition_name}"
    
#     # class Meta:
#     #     verbose_name_plural = "Medical histories"

# class Allergy(models.Model):
#     """Patient's allergies"""
    
#     SEVERITY_CHOICES = (
#         ('MILD', 'Mild'),
#         ('MODERATE', 'Moderate'),
#         ('SEVERE', 'Severe'),
#     )
    
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='allergies')
#     allergy_name = models.CharField(max_length=100)
#     reaction = models.TextField(blank=True, null=True)
#     severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MILD')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s allergy to {self.allergy_name}"
    
#     class Meta:
#         verbose_name_plural = "Allergies"

# class Medication(models.Model):
#     """Current medications taken by the patient"""
    
#     FREQUENCY_CHOICES = (
#         ('DAILY', 'Daily'),
#         ('TWICE_DAILY', 'Twice Daily'),
#         ('THREE_TIMES', 'Three Times a Day'),
#         ('FOUR_TIMES', 'Four Times a Day'),
#         ('WEEKLY', 'Weekly'),
#         ('AS_NEEDED', 'As Needed'),
#         ('OTHER', 'Other'),
#     )
    
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medications')
#     medication_name = models.CharField(max_length=100)
#     dosage = models.CharField(max_length=50)
#     frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES)
#     start_date = models.DateField()
#     end_date = models.DateField(blank=True, null=True)
#     purpose = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s medication: {self.medication_name}"

# class FamilyMedicalHistory(models.Model):
#     """Patient's family medical history"""
    
#     RELATIONSHIP_CHOICES = (
#         ('FATHER', 'Father'),
#         ('MOTHER', 'Mother'),
#         ('BROTHER', 'Brother'),
#         ('SISTER', 'Sister'),
#         ('GRANDFATHER_P', 'Paternal Grandfather'),
#         ('GRANDMOTHER_P', 'Paternal Grandmother'),
#         ('GRANDFATHER_M', 'Maternal Grandfather'),
#         ('GRANDMOTHER_M', 'Maternal Grandmother'),
#         ('OTHER', 'Other'),
#     )
    
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='family_medical_histories')
#     relationship = models.CharField(max_length=15, choices=RELATIONSHIP_CHOICES)
#     condition_name = models.CharField(max_length=200)
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s {self.relationship}: {self.condition_name}"
    
#     class Meta:
#         verbose_name_plural = "Family medical histories"

# class Document(models.Model):
#     """Medical documents uploaded by the patient"""
    
#     DOCUMENT_TYPE_CHOICES = (
#         ('LAB_REPORT', 'Lab Report'),
#         ('PRESCRIPTION', 'Prescription'),
#         ('DISCHARGE_SUMMARY', 'Discharge Summary'),
#         ('IMAGING', 'Imaging/Scan Report'),
#         ('INSURANCE', 'Insurance Document'),
#         ('OTHER', 'Other'),
#     )
    
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='documents')
#     document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
#     title = models.CharField(max_length=200)
#     file = models.FileField(upload_to='patient_documents/')
#     date_of_record = models.DateField()
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s {self.get_document_type_display()}: {self.title}"

# class PatientPreference(models.Model):
#     """Patient preferences for appointments and notifications"""
    
#     REMINDER_CHOICES = (
#         ('EMAIL', 'Email'), # Choose, whatsapp
#         ('SMS', 'SMS'), # Choose
#         ('PUSH', 'Push Notification'),  # Default
#         ('ALL', 'All'),
#         # ('NONE', 'None'),
#     )
    
#     patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE, related_name='preferences')
#     preferred_appointment_time = models.CharField(max_length=20, blank=True, null=True)
#     preferred_communication = models.CharField(max_length=10, choices=REMINDER_CHOICES, default='ALL')
#     reminder_before_hours = models.IntegerField(default=24)
#     receive_promotional_notifications = models.BooleanField(default=True)
#     # receive_health_tips = models.BooleanField(default=True)
#     language_preference = models.CharField(max_length=10, default='English')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.patient.user.first_name}'s Preferences"