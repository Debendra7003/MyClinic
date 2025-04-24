from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LabReport
from MyClinic.utils import send_push_notification

@receiver(post_save, sender=LabReport)
def notify_lab_report_ready(sender, instance, created, **kwargs):
    """
    Sends a push notification to the patient when a lab report is created.
    """
    if created:
        patient = instance.lab_test.patient
        registration_token = patient.user.firebase_registration_token
        if registration_token:
            title = "Lab Report Ready"
            body = f"Your lab report for {instance.lab_test.test_type} is now available."
            send_push_notification(registration_token, title, body)

        
     # SMS Notification
        # if patient.user.mobile_number:
        #     sms_body = f"Hi {patient.user.first_name}, your lab report for {instance.lab_test.test_type} is ready. Please check your account."
        #     send_sms(patient.user.mobile_number, sms_body)