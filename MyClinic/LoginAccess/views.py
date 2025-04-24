from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserLogin
from django.contrib.auth import authenticate
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .firebase_auth import FirebaseAuthentication
from .models import User

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
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
    



    # FIREBASE USE


#     class UserLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, format=None):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#             return Response({'error': 'Authorization header is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Authenticate using Firebase
#             firebase_auth = FirebaseAuthentication()
#             user, _ = firebase_auth.authenticate(request)

#             # Generate JWT tokens for the user
#             token = get_tokens_for_user(user)
#             response_data = {
#                 'user_id': user.user_id,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'email': user.email,
#                 'mobile_number': user.mobile_number,
#                 'role': user.role,
#                 'is_admin': user.is_admin,
#                 'Token': token,
#             }
#             return Response({'msg': "Login Successful", 'user': response_data}, status=status.HTTP_200_OK)
#         except AuthenticationFailed as e:
#             return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        

# class UserRegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         firebase_auth = FirebaseAuthentication()
#         auth_header = request.headers.get('Authorization')

#         if not auth_header:
#             return Response({'error': 'Authorization header is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Authenticate using Firebase
#             user, _ = firebase_auth.authenticate(request)

#             # Check if the user already exists
#             if User.objects.filter(email=user.email).exists():
#                 return Response({"message": "User already registered."}, status=status.HTTP_400_BAD_REQUEST)

#             # Save the user in the database
#             serializer = UserSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
#             return Response({"message": "User registration failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except AuthenticationFailed as e:
#             return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
