from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserLogin, GoogleSignInSerializer, FirebaseTokenSerializer, EmailOTPVerifySerializer
from django.contrib.auth import authenticate
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from twilio.rest import Client
from django.db import transaction
from django.core.mail import send_mail
from .models import User
from django.utils import timezone
from django.contrib.auth.hashers import check_password

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}

def send_email_otp(customer):
    try:
        
        otp = customer.email_otp
        recipient_email = customer.email 

        subject = "Verify Your Email with OTP"
        message = (
            f"Hi {customer.first_name},\n\n"
            f"Your OTP to verify your email is: {otp}\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Thank you,\nEzydoc Team"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)
    except Exception as e:
        # Optional: You can log the error
        print(f"Email OTP sending failed: {str(e)}")

def send_sms_otp(customer):
    try:
        otp = customer.otp
        print("Mobile OTP:", otp)
        recipient_number = customer.mobile_number  # Fallback to current number if no temp update
        if not recipient_number.startswith('+91'):
            recipient_number = '+91' + recipient_number.lstrip('0')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Hi {customer.first_name}, your OTP for SMS verification is: {otp}. Valid for 5 minutes.",
            from_=settings.SMS_SENDER_ID,
            to=recipient_number
        )
    except Exception as e:
        # Optional: You can log the error
        print(f"SMS OTP sending failed: {str(e)}")

class EmailOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            serializer = EmailOTPVerifySerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                user.is_active = True
                user.email_otp = None  # Clear OTP after verification
                user.save()
                return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# SMS OTP Verification
class SMSOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        mobile_number = request.data.get("mobile_number")
        sms_otp = request.data.get("otp")
        try:
            customer = User.objects.get(mobile_number=mobile_number)
            if customer.verification_expiry < timezone.now():
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
            if customer.otp == sms_otp:
                customer.is_active = True
                customer.otp = None
                customer.save()
                return Response({
                    "message": "SMS OTP verified successfully",
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    email = serializer.validated_data.get('email')
                    mobile_number = serializer.validated_data.get('mobile_number')
                    if email:
                        user.set_email_otp()
                        send_email_otp(user)
                    if mobile_number:
                        user.set_sms_otp()
                        send_sms_otp(user)
                message = f"Registration successful, please verify."
                # if email:
                #     message += "your email with OTP"
                # elif mobile_number:
                #     message += "your mobile number with OTP"
                return Response({'msg': message}, status=status.HTTP_201_CREATED)
            # serializer.save()
            # return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Error during user registration: {e}")
                return Response({"message": "User registration failed.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "User registered Failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes= [AllowAny]
    def post(self, request, format=None):
        print(request.data)
        serializer = UserLogin(data=request.data)
        # print(serializer.is_valid())
        # print(serializer.errors)
        if serializer.is_valid(raise_exception=True):
            mobile_number = serializer.validated_data['mobile_number']
            password = serializer.validated_data['password']
            # mobile_number = serializer.data.get('mobile_number')
            # password = serializer.data.get('password')
            print("Views: ", password)
            user = authenticate(request=request,mobile_number=mobile_number, password=password)
            print("Views: ",user)
            if user is not None:
                if not user.is_active:
                    return Response({'Errors': {'non_field_errors': ['Your account is not active. Please verify your email or mobile number.']}}, status=status.HTTP_403_FORBIDDEN)
                response_data = {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'role': user.role,
                    'is_admin': user.is_admin
                }
                token = get_tokens_for_user(user)
                return Response({'msg': "Login Successful", 'user': response_data, 'Token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'Errors': {'non_field_errors': ['Mobile number or password is not valid']}}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FirebaseTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FirebaseTokenSerializer(data=request.data)
        if serializer.is_valid():
            firebase_token = serializer.validated_data['firebase_registration_token']
            user = request.user
            user.firebase_registration_token = firebase_token
            user.save()
            return Response({'message': 'Firebase registration token updated successfully.'}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class GoogleSignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleSignInSerializer(data=request.data)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            response_data = {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile_number': user.mobile_number,
                'role': user.role,
                'is_admin': user.is_admin
            }
            token = get_tokens_for_user(user)
            return Response(
                {'msg': "Google Sign-In Successful", 'user': response_data, 'Token': token},
                status=status.HTTP_200_OK
            )
        return Response({'msg': "Google Sign-In Failed", 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)







class PasswordResetRequestOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')
        
        if not email and not mobile_number:
            return Response({"error": "Please provide either email or mobile number"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = None
            if email:
                customer = User.objects.get(email=email)
                if not customer.is_active:
                    return Response({"error": "Email is not verified. Please verify your email first."}, 
                                  status=status.HTTP_403_FORBIDDEN)
                customer.set_email_otp()
                send_email_otp(customer)
                return Response({"message": "OTP sent to your email"}, 
                              status=status.HTTP_200_OK)
            elif mobile_number:
                customer = User.objects.get(mobile_number=mobile_number)
                if not customer.is_active:
                    return Response({"error": "Mobile number is not verified. Please verify your mobile number first."}, 
                                  status=status.HTTP_403_FORBIDDEN)
                customer.set_sms_otp()
                send_sms_otp(customer)
                return Response({"message": "OTP sent to your mobile number"}, 
                              status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # identifier = request.data.get('identifier')  # email or mobile_number
        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')
        otp = request.data.get('otp')
        
        try:
            customer = None
            if email:  #  an email
                customer = User.objects.get(email=email)
                if customer.email_otp != otp or customer.verification_expiry < timezone.now():
                    return Response({"error": "Invalid or expired OTP"}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                customer.email_otp = None
                customer.can_reset_password = True
            else:  # Assuming it's a mobile number
                customer = User.objects.get(mobile_number=mobile_number)
                print("Customer:", customer.otp)
                print("OTP:", otp)
                print("Verification Expiry:", customer.verification_expiry)
                print("Current Time:", timezone.now())
                # print(customer.verification_expiry < timezone.now())
                print(customer.otp != otp)
                if customer.otp != otp or customer.verification_expiry < timezone.now():
                    return Response({"error": "Invalid or expired OTP"}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                customer.otp = None
                customer.can_reset_password = True
            
            customer.save()
            return Response({"message": "OTP verified successfully"}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, 
                          status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # identifier = request.data.get('identifier')
        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')
        new_password = request.data.get('new_password')
        
        try:
            customer = None
            if email:
                customer = User.objects.get(email=email)
            else:
                customer = User.objects.get(mobile_number=mobile_number)
            
            if not customer.can_reset_password:
                return Response({"error": "OTP verification is required before resetting the password"}, 
                              status=status.HTTP_403_FORBIDDEN)
            customer.set_password(new_password)
            customer.can_reset_password = False
            customer.save()
            return Response({"message": "Password reset successful"}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, 
                          status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({"error": "Both current and new passwords are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not check_password(current_password, user.password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)





# class GoogleSignInView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = GoogleSignInSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             response_data = {
#                 'user_id': user.user_id,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'email': user.email,
#                 'mobile_number': user.mobile_number,
#                 'role': user.role,
#                 'is_admin': user.is_admin
#             }
#             token = get_tokens_for_user(user)
#             return Response(
#                 {'msg': "Google Sign-In Successful", 'user': response_data, 'Token': token},
#                 status=status.HTTP_200_OK
#             )
#         return Response({'msg': "Google Sign-In Failed", 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)