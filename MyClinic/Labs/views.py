from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import LabTest, LabReport, LabProfile, LabType, LabAvailability
from .serializers import LabTestSerializer, LabReportSerializer, LabProfileSerializer, LabTypeSerializer, LabAvailabilitySerializer
from Patients.models import PatientProfile
from rest_framework import serializers
from rest_framework.permissions import BasePermission
from MyClinic.permissions import IsLab, IsPatient, IsReadOnly, IsAdmin
from datetime import datetime, timedelta
from MyClinic.utils import send_scheduled_push_notification
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from django.db import models
from DoctorAccess.models import DoctorRegistration
from LoginAccess.models import User
from rest_framework import status

def schedule_lab_test_notifications(lab_test):
    patient = lab_test.patient
    registration_token = patient.user.firebase_registration_token
    print(f"Registration_Token: {registration_token}")
    if registration_token:

        # 1 day before
        send_scheduled_push_notification(
            registration_token=registration_token,
            title="Lab Test Reminder",
            body=f"Your lab test for {lab_test.test_type} is scheduled tomorrow at {lab_test.scheduled_date}.",
            delivery_time=lab_test.scheduled_date - timedelta(days=1),
        )

        # 2 hours before
        send_scheduled_push_notification(
            registration_token=registration_token,
            title="Lab Test Reminder",
            body=f"Your lab test for {lab_test.test_type} is scheduled in 2 hours at {lab_test.scheduled_date}.",
            delivery_time=lab_test.scheduled_date - timedelta(hours=2),
        )

        # 1 hour before
        send_scheduled_push_notification(
            registration_token=registration_token,
            title="Lab Test Reminder",
            body=f"Your lab test for {lab_test.test_type} is scheduled in 1 hour at {lab_test.scheduled_date}.",
            delivery_time=lab_test.scheduled_date - timedelta(hours=1),
        )

class LabProfileViewSet(viewsets.ModelViewSet):
    queryset = LabProfile.objects.all()
    serializer_class = LabProfileSerializer
    permission_classes = [IsLab | IsReadOnly] # Labs can modify, others can view
    
    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return LabProfile.objects.none()

        if user.role == 'lab':
        # Lab user: only their own profile
            return LabProfile.objects.filter(user=user)
        elif getattr(user, 'is_admin', False):
        # Admin: all profiles
            return LabProfile.objects.all()
        elif user.role == 'patient':
        # Patient: all profiles (or return LabProfile.objects.none() to restrict)
            return LabProfile.objects.all()
        else:
            return LabProfile.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only labs can create a lab profile.")
        if LabProfile.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("A LabProfile already exists for this lab.")
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.user)
        if instance.user != request.user:
            raise serializers.ValidationError("You are not authorized to update this lab profile.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        if instance.user != request.user:
            raise serializers.ValidationError("You are not authorized to delete this lab profile.")
        return super().destroy(request, *args, **kwargs)
    


class LabTypeViewSet(viewsets.ModelViewSet):
    queryset = LabType.objects.all()
    serializer_class = LabTypeSerializer
    permission_classes = [IsLab | IsReadOnly] # Labs can modify, others can view
    
    def get_queryset(self):
        queryset = LabType.objects.all()
        location = self.request.query_params.get('location', None)
        if location:
            # Filter LabTypes that have at least one LabProfile with matching location or blank/null
            queryset = queryset.filter(
                labs__location__icontains=location
            # ) | queryset.filter(
            #     labs__location__isnull=True
            # ) | queryset.filter(
            #     labs__location__exact=''
            )
            queryset = queryset.distinct()
        return queryset
    def perform_create(self, serializer):
        # lab_type = serializer.save()
        # if hasattr(self.request.user, 'lab_profile'):
        #     lab_type.lab_profiles.add(self.request.user.lab_profile)
        # else:
        #     raise serializers.ValidationError("Only labs can create lab types.")
        # if not hasattr(self.request.user, 'lab_profile'):
        #     raise serializers.ValidationError("Only labs can create lab types.")
        # serializer.save(lab_profile=self.request.user.lab_profile)
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.lab_profile.user != request.user or self.request.user.role != 'lab':
        #     raise serializers.ValidationError("You are not authorized to update this lab type.")
        if not hasattr(request.user, 'lab_profile') or request.user.lab_profile not in instance.lab_profiles.all():
            raise serializers.ValidationError("You are not authorized to update this lab type.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.lab_profile.user != request.user or self.request.user.role != 'lab':
        #     raise serializers.ValidationError("You are not authorized to delete this lab type.")
        if not hasattr(request.user, 'lab_profile') or request.user.lab_profile not in instance.lab_profiles.all():
            raise serializers.ValidationError("You are not authorized to update this lab type.")
        return super().destroy(request, *args, **kwargs)


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsPatient | IsLab | IsAdmin] # Patients can book, labs can view/manage

    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = ['lab_profile__name', 'test_type']
    # search_fields = ['lab_profile__name', 'test_type']

    def get_queryset(self):
        user = self.request.user
        registration_number = self.request.query_params.get('registration_number', None)
        if registration_number:
            return LabTest.objects.filter(registration_number=registration_number)
        if user.role == 'lab':
            if hasattr(user, 'lab_profile'):
                return LabTest.objects.filter(lab_profile=user.lab_profile)
            return LabTest.objects.none()
            # return LabTest.objects.filter(patient__user__role="patient")
        elif user.role == 'patient':
            return LabTest.objects.filter(patient__user=user)
        
        elif user.is_admin:
            return LabTest.objects.all()
        
        return LabTest.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'patient':
            raise serializers.ValidationError("Only patients can book lab tests.")
        try:
            patient_profile = PatientProfile.objects.get(user=self.request.user)
            lab_profile = LabProfile.objects.get(id=self.request.data.get('lab_profile'))
            lab_test_store = serializer.save(patient=patient_profile, lab_profile=lab_profile)
            schedule_lab_test_notifications(lab_test_store)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("No patient profile found for the current user.")
        except LabProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid lab profile ID.")
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.role == 'lab' and instance.lab_profile != user.lab_profile:
            raise serializers.ValidationError("You are not authorized to update this lab test.")
        elif user.role == 'patient' and instance.patient.user != user:
            raise serializers.ValidationError("You are not authorized to update this lab test.")

        # Perform the update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        # Trigger notifications if the scheduled_date is updated
        if 'scheduled_date' in serializer.validated_data:
            schedule_lab_test_notifications(updated_instance)

        return Response(serializer.data)




class LabAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = LabAvailability.objects.all()
    serializer_class = LabAvailabilitySerializer
    permission_classes = [IsLab | IsPatient | IsAdmin]

    def get_queryset(self):
        if self.request.user.role == 'patient' or self.request.user.is_admin:
            return LabAvailability.objects.all()
        elif self.request.user.role == 'lab':
            return LabAvailability.objects.filter(lab=self.request.user)
        return LabAvailability.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)
        # Check if data is a list (bulk) or dict (single)
        is_many = isinstance(data, list)
        if is_many:
            for item in data:
                item['lab'] = self.request.user.user_id  # Set lab for each item
            serializer = self.get_serializer(data=data, many=True)
        else:
            data['lab'] = self.request.user.user_id
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        if isinstance(serializer.validated_data, list):
            lab_instance = self.request.user  # This is the User instance
            to_create = []
            duplicates = []
            for item in serializer.validated_data:
                date = item['date']
                start_time = item['start_time']
                end_time = item['end_time']
                exists = LabAvailability.objects.filter(
                    lab=lab_instance,
                    date=date,
                    # start_time=start_time,
                    # end_time=end_time,
                ).exists()
                if exists:
                    duplicates.append(f"{date} {start_time}-{end_time}")
                else:
                    to_create.append(
                    LabAvailability(
                        lab=lab_instance,
                        **{k: v for k, v in item.items() if k != 'lab'}
                    )
                )
            if duplicates:
                print(f"Duplicates found: {duplicates}")
                raise serializers.ValidationError(
                {"error": f"Availability already exists for: {', '.join(duplicates)}"}
            )
            if to_create:
                LabAvailability.objects.bulk_create(to_create)
        else:
            serializer.save(lab=self.request.user)

    # def perform_create(self, serializer):
    #     try:
    #         if self.request.user.role != 'doctor':
    #             raise ValidationError({
    #                 "error": "Only doctors are allowed to create availability."
    #             })
    #         serializer.save(doctor=self.request.user)

    #     except IntegrityError:
    #         raise ValidationError({
    #             "error": "This availability already exists for the selected date, shift and time."
    #         })
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.role == 'doctor':
            raise serializers.ValidationError("You are not authorized to update.")
        elif user.role == 'patient':
            raise serializers.ValidationError("You are not authorized to update.")

        # Perform the update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.role != 'lab':
            raise serializers.ValidationError("You are not authorized to delete this availability.")

        self.perform_destroy(instance)
        return Response({"message": "Availability deleted successfully."}, status=status.HTTP_200_OK)




class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [IsLab | IsPatient]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'lab':
            if hasattr(user, 'lab_profile'):
                return LabReport.objects.filter(lab_test__lab_profile=user.lab_profile)

            return LabReport.objects.none()

            # return LabReport.objects.filter(lab_test__patient__user__role="patient")

        elif user.role == 'patient':
            return LabReport.objects.filter(lab_test__patient__user=user)
        return LabReport.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'lab':
            raise serializers.ValidationError("Only labs can upload reports.")
        
        lab_test_id = self.request.data.get('lab_test')
        if not lab_test_id:
            raise serializers.ValidationError({"lab_test": "This field is required."})
        
        try:
            lab_test = LabTest.objects.get(id=lab_test_id)
            if lab_test.lab_profile != self.request.user.lab_profile:
                raise serializers.ValidationError("You are not authorized to upload a report for this lab test.")
            serializer.save(lab_test=lab_test)
        except LabTest.DoesNotExist:
            raise serializers.ValidationError("No lab test found with the provided ID.")
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_test.lab_profile != request.user.lab_profile:
            raise serializers.ValidationError("You are not authorized to update this lab report.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.lab_test.lab_profile != request.user.lab_profile:
            raise serializers.ValidationError("You are not authorized to delete this lab report.")
        return super().destroy(request, *args, **kwargs)


class LabProfileFilter(filters.FilterSet):
    tests = filters.CharFilter(field_name='lab_types__tests', lookup_expr='icontains')  # Custom filter for JSONField

    class Meta:
        model = LabProfile
        fields = {
            'name': ['icontains'],  
            'lab_types__name': ['icontains'], 
        }
        filter_overrides = {
            models.JSONField: {
                'filter_class': filters.CharFilter,  
                'extra': lambda f: {
                    'lookup_expr': 'icontains',  
                },
            },
        }


class LabSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LabProfile.objects.all()
    serializer_class = LabProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = LabProfileFilter
    filterset_fields = ['name', 'lab_types__name', 'lab_types__tests']
    search_fields = ['name', 'lab_types__name', 'lab_types__tests']

    def get_queryset(self):
        return LabProfile.objects.prefetch_related('lab_types')
    
 

class CentralSearchView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        query = request.GET.get('q', '')
        # Doctor search
        doctors = DoctorRegistration.objects.filter(
            models.Q(doctor_name__icontains=query) |
            models.Q(specialist__icontains=query) |
            models.Q(doctor__first_name__icontains=query) |
            models.Q(doctor__last_name__icontains=query)
)
        
        doctor_users = User.objects.filter(
            role='doctor'
        ).filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        )
        # Lab search
        labs = LabProfile.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(lab_types__name__icontains=query) |
            models.Q(lab_types__tests__icontains=query)
        ).distinct()
        # LabType search
        lab_types = LabType.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(tests__icontains=query)
        ).distinct()

        from DoctorAccess.serializers import DoctorRegistrationSerializer
        from Labs.serializers import LabProfileSerializer, LabTypeSerializer
        from LoginAccess.serializers import UserSerializer

        return Response({
            "doctors": DoctorRegistrationSerializer(doctors, many=True).data,
            "labs": LabProfileSerializer(labs, many=True).data,
            "lab_types": LabTypeSerializer(lab_types, many=True).data,
            "doctor_users": UserSerializer(doctor_users, many=True).data,
        })