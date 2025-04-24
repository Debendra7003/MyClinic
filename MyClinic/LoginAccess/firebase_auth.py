from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        token = auth_header.split(' ').pop()
        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', None)
            phone_number = decoded_token.get('phone_number', None)

            # Get or create the user in the database
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'mobile_number': phone_number,
                    'first_name': decoded_token.get('name', ''),
                    'role': 'patient',  # Default role, can be updated later
                }
            )
            return (user, None)
        except Exception as e:
            raise AuthenticationFailed('Invalid Firebase token')