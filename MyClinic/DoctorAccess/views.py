from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from .models import DoctorRegistration
from rest_framework.permissions import AllowAny
from .serializers import DoctorRegistrationSerializer
# from rest_framework.permissions import IsAuthenticated




class DoctorRegistrationView(APIView):
    permission_classes =  [AllowAny] # or[IsAuthenticated]  

    def post(self, request, format=None):
        serializer = DoctorRegistrationSerializer(data=request.data)
        print(request.data)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            # serializer.save()
            # serializer.validated_data.pop('user_id')
            print(serializer.validated_data)
            serializer.save()
            return Response({"message": "Doctor profile registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
