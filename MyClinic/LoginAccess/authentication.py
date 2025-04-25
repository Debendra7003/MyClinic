from django.contrib.auth.backends import ModelBackend
from .models import User
import firebase_admin
from firebase_admin import auth
from rest_framework import authentication
from rest_framework import exceptions
from .models import User
from .models import generate_customer_id

class CustomAuthBackend(ModelBackend):
    def authenticate(self,request,mobile_number=None,password=None,**kwargs):
        try:
            if mobile_number:
                user = User.objects.get(mobile_number=mobile_number)
               
            else:
                return None
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        




class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token.get("uid")
        except (IndexError, ValueError, auth.InvalidIdTokenError, auth.ExpiredIdTokenError) as e:
            raise exceptions.AuthenticationFailed(f"Invalid Firebase token: {str(e)}")

        try:
            # Try to find user by firebase_uid or email
            user = None
            if firebase_uid:
                user = User.objects.filter(firebase_uid=firebase_uid).first()
            if not user and decoded_token.get('email'):
                user = User.objects.filter(email=decoded_token['email']).first()

            if not user:
                # Create new user
                user = User.objects.create_user(
                    mobile_number=decoded_token.get('email', f"{firebase_uid}@example.com"),
                    firebase_uid=firebase_uid,
                    email=decoded_token.get('email'),
                    first_name=decoded_token.get('name', '').split(' ')[0] if decoded_token.get('name') else '',
                    last_name=' '.join(decoded_token.get('name', '').split(' ')[1:]) if decoded_token.get('name') else '',
                    role='patient',
                    user_id=generate_customer_id()
                )
            return (user, None)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Error processing user: {str(e)}")
