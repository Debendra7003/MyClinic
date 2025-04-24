from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ambulance
from .serializers import AmbulanceSerializer
from django.db.models import Count
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from LoginAccess.models import User


# Create your views here.


class AmbulanceView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = AmbulanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ambulance registered successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ToggleAmbulanceStatusView(APIView):
    permission_classes=[AllowAny]
    def put(self, request, ambulance_id, vehicle_number):
        try:
            user = get_object_or_404(User, user_id=ambulance_id)
            ambulance = Ambulance.objects.get(ambulance_id=user, vehicle_number=vehicle_number)
        except Ambulance.DoesNotExist:
            return Response({"error": "Ambulance not found with provided ambulance_id and vehicle_number."}, status=status.HTTP_404_NOT_FOUND)

        ambulance.active = not ambulance.active  # Toggle active status
        ambulance.save()

        return Response({
            "message": f"Ambulance status updated to {'Active' if ambulance.active else 'Inactive'}",}, status=status.HTTP_200_OK)
    

class AmbulanceByUserView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, ambulance_id):
        # Check if the user exists
        user = get_object_or_404(User, user_id=ambulance_id)
        # Get ambulances for this user
        ambulances = Ambulance.objects.filter(ambulance_id=user)
        active_ambulances = ambulances.filter(active=True)
        inactive_ambulances = ambulances.filter(active=False)
        # active_serializer = AmbulanceSerializer(active_ambulances, many=True)
        # inactive_serializer = AmbulanceSerializer(inactive_ambulances, many=True)
        return Response({
            "active_count": active_ambulances.count(),
            "inactive_count": inactive_ambulances.count()
        }, status=status.HTTP_200_OK)
    

class AmbulanceStatusFilterView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        active_param = request.GET.get('active')  # ?active=true or false

        if active_param is not None:
            if active_param.lower() == "true":
                ambulances = Ambulance.objects.filter(active=True)
                status_label = "active"
            elif active_param.lower() == "false":
                ambulances = Ambulance.objects.filter(active=False)
                status_label = "inactive"
            else:
                return Response({"error": "Invalid value for 'active'. Use 'true' or 'false'."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ambulances = Ambulance.objects.all()
            status_label = "all"

        serializer = AmbulanceSerializer(ambulances, many=True)
        return Response({
            "status": status_label,
            "ambulances": serializer.data
        }, status=status.HTTP_200_OK)


class AmbulanceDeleteView(APIView):
    permission_classes=[AllowAny]
    def delete(self, request, ambulance_id, vehicle_number):
        # Get the user by custom user_id
        user = get_object_or_404(User, user_id=ambulance_id)

        try:
            ambulance = Ambulance.objects.get(
                ambulance_id=user,
                vehicle_number=vehicle_number
            )
        except Ambulance.DoesNotExist:
            return Response({
                "error": f"No ambulance found for vehicle '{vehicle_number}' under user '{ambulance_id}'"
            }, status=status.HTTP_404_NOT_FOUND)

        ambulance.delete()
        return Response({
            "message": f"Ambulance with vehicle '{vehicle_number}' deleted successfully"
        }, status=status.HTTP_200_OK)