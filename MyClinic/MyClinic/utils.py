from firebase_admin import messaging
from twilio.rest import Client
from django.conf import settings
from datetime import datetime, timedelta

def send_push_notification(registration_token, title, body, data=None):
    """
    Send push notification to a specific device using Firebase Cloud Messaging (FCM).
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=registration_token,
            data=data or {},
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
            data=data or {},
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
