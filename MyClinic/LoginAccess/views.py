from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserLogin, GoogleSignInSerializer, FirebaseTokenSerializer
from django.contrib.auth import authenticate
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
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