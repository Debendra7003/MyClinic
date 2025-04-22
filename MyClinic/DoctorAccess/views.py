from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DoctorRegistrationSerializer
from .models import DoctorRegistration
from LoginAccess.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
# from rest_framework.permissions import IsAuthenticated




class DoctorRegistrationView(APIView):
    permission_classes=[AllowAny]
    def post(self, request, format=None):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    "message": "Doctor registered successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({
                    "error": "Integrity error occurred (likely duplicate license number)",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DoctorProfileAPIView(APIView):
    permission_classes = [AllowAny]

#------------------------------------------------- Doctor get-all or get by ID functionality----------------------------------------------------------------
    def get(self, request, doctor_id=None):
        if doctor_id:
            doctor_instance = get_object_or_404(User, user_id=doctor_id)
            try:
                profile = DoctorRegistration.objects.get(doctor=doctor_instance)
                serializer = DoctorRegistrationSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DoctorRegistration.DoesNotExist:
                return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            profiles = DoctorRegistration.objects.all()
            serializer = DoctorRegistrationSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        

#------------------------------------------------- Doctor Update functionality------------------------------------------------------------------------
    def put(self, request, doctor_id): 
        user = get_object_or_404(User, user_id=doctor_id)
        try:
            profile = DoctorRegistration.objects.get(doctor=user)
        except DoctorRegistration.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DoctorRegistrationSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#------------------------------------------------- Doctor Delete functionality-------------------------------------------------------------------------
    def delete(self, request, doctor_id):
        user = get_object_or_404(User, user_id=doctor_id)
        try:
            profile = DoctorRegistration.objects.get(doctor=user)
            profile.delete()
            return Response({"message": "Doctor profile deleted successfully"}, status=status.HTTP_200_OK)
        except DoctorRegistration.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)