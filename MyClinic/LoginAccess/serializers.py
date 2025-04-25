from rest_framework import serializers
from .models import User
import firebase_admin
from firebase_admin import auth
from .models import generate_customer_id


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'mobile_number',
            'password', 'password2', 'role','firebase_registration_token']
        
        read_only_fields = ['user_id', 'is_active', 'created_at']

    def validate(self, data):
        #Validate password and password2 match
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        #Remove password2 before saving
        password = validated_data.pop('password')
        validated_data.pop('password2')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
class UserLogin(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)
    def validate(self,data):
        if not data['password']:
            raise serializers.ValidationError("Password Field Required")
        if not data['mobile_number']:
            raise serializers.ValidationError("Mobile Number Field Required")
        user = None
        user = User.objects.filter(mobile_number=data['mobile_number']).first()
        if user is None:
            raise serializers.ValidationError("Invalid Login Credentials")
        data['user'] = user
        return data
    # class Meta:
    #     model=User
    #     fields=['mobile_number','password']


class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

    def validate(self, data):
        id_token = data.get('id_token')
        try:
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')

            # Try to find user by firebase_uid or email
            user = User.objects.filter(firebase_uid=firebase_uid).first()
            if not user and email:
                user = User.objects.filter(email=email).first()

            if not user:
                # Create new user
                user = User.objects.create_user(
                    mobile_number=email or f"{firebase_uid}@example.com",
                    firebase_uid=firebase_uid,
                    email=email,
                    first_name=name.split(' ')[0] if name else '',
                    last_name=' '.join(name.split(' ')[1:]) if name else '',
                    role=data.get('role', 'patient'),
                    user_id=generate_customer_id()
                )
            else:
                # Update role if provided
                user.role = data.get('role', user.role)
                user.save()
            data['user'] = user
            return data
        except auth.InvalidIdTokenError:
            raise serializers.ValidationError("Invalid Google token")
        except auth.ExpiredIdTokenError:
            raise serializers.ValidationError("Google token has expired")
        except Exception as e:
            raise serializers.ValidationError(f"Google Sign-In failed: {str(e)}")