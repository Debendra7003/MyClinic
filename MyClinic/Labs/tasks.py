from celery import shared_task
from MyClinic.utils import send_push_notification

@shared_task
def send_lab_test_reminder(registration_token, title, body, data=None):
    send_push_notification(registration_token, title, body, data)