from firebase_admin import messaging
from twilio.rest import Client
from django.conf import settings
from datetime import datetime, timedelta
from django.core.mail import send_mail

def send_push_notification(registration_token, title, body,image=None, data=None):
    """
    Send push notification to a specific device using Firebase Cloud Messaging (FCM).
    """
    try:
        message = messaging.Message(
            token=registration_token,
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image,
            ),
            data={
        "title": title,
        "body": body,
        **(data or {})
    },
            # data=data or {},
        )
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return None



def send_scheduled_push_notification(registration_token, title, body, delivery_time, data=None):
    """
    Send a scheduled push notification using Firebase Cloud Messaging (FCM).
    """
    try:
        # Convert delivery_time to ISO 8601 format
        if isinstance(delivery_time, datetime.date) and not isinstance(delivery_time, datetime.datetime):
            delivery_time = datetime.combine(delivery_time, datetime.min.time())
        delivery_time_iso = delivery_time.isoformat() + "Z"
        print("Scheduled Working..")
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=registration_token,
            android=messaging.AndroidConfig(
                ttl=timedelta(days=1),  # Time-to-live for the message
                restricted_package_name=None,
                priority="high",
            ),
            apns=messaging.APNSConfig(
                headers={
                    "apns-expiration": str(int(delivery_time.timestamp()))
                }
            ),
            data={
        "title": title,
        "body": body,
        **(data or {})
    },
            # data=data or {},
        )
        response = messaging.send(message)
        return response
    
    except Exception as e:
        print(f"Error sending scheduled push notification: {e}")
        return None
    

def send_sms(to_number, message_body):
    """
    Sends an SMS using Twilio.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.SMS_SENDER_ID,
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def send_email_message(subject, message, recipient_list, from_email=None, fail_silently=False, html_message=None):
            """
            Sends an email using send_mail function.
            """
            try:
                result = send_mail(
                    subject,
                    message,
                    from_email or settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=fail_silently,
                    html_message=html_message
                )
                return result
            except Exception as e:
                print(f"Error sending email: {e}")
                return None