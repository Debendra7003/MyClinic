from rest_framework import serializers
from .models import LabTest, LabReport, LabProfile, LabType, LabAvailability
from Patients.serializers import PatientProfileSerializer
from django.db.models.functions import TruncMinute
from django.utils.timezone import is_naive, make_aware
from datetime import datetime, timezone


class SimpleLabProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabProfile
        fields = ['id','user','home_sample_collection', 'name', 'address','location', 'phone']


class LabTypeSerializer(serializers.ModelSerializer):
    lab_profiles = SimpleLabProfileSerializer(source="labs",many=True, read_only=True)
    class Meta:
        model = LabType
        fields = ['id', 'name', 'tests', 'lab_profiles']
        read_only_fields = ['id']

class LabProfileSerializer(serializers.ModelSerializer):
     # For write (input)
    lab_types = serializers.PrimaryKeyRelatedField(queryset=LabType.objects.all(), many=True, write_only=True)
    # For read (output)
    lab_types_details = LabTypeSerializer(source='lab_types', many=True, read_only=True)
    class Meta:
        model = LabProfile
        fields = ['id', 'user', 'name', 'lab_types','lab_types_details','address','location', 'phone', 'home_sample_collection', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    def create(self, validated_data):
        lab_types = validated_data.pop('lab_types', [])
        lab_profile = LabProfile.objects.create(**validated_data)
        lab_profile.lab_types.set(lab_types)
        return lab_profile

    def update(self, instance, validated_data):
        lab_types = validated_data.pop('lab_types', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lab_types is not None:
            instance.lab_types.set(lab_types)
        return instance




class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = ['id', 'file', 'description', 'published_at','lab_test']
    
    def validate(self, data):
        if self.context['request'].user.role != 'lab':
            raise serializers.ValidationError("Only labs can upload reports.")
        return data

class LabTestSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(read_only=True)
    reports = LabReportSerializer(many=True, read_only=True)
    lab_profile = serializers.PrimaryKeyRelatedField(queryset=LabProfile.objects.all())
    patient_name = serializers.SerializerMethodField()  
    lab_profile_name = serializers.SerializerMethodField()
    lab_profile_code = serializers.SerializerMethodField()

    class Meta:
        model = LabTest
        fields = ['id', 'patient','patient_name', 'lab_profile','lab_profile_code', 'lab_profile_name', 'test_type', 'scheduled_date', 'registration_number' ,'status', 'created_at', 'reports']
    
    # def round_to_minute(self,dt):
    #     return dt.replace(second=0, microsecond=0) if dt else None
    def round_to_minute(self, dt):
        if dt is None:
            return None
        dt = dt.replace(second=0, microsecond=0)
        # Ensure timezone-aware for comparison with DB
        if is_naive(dt):
            from django.conf import settings
            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            dt = make_aware(dt, timezone=tz)
        return dt

    def validate(self, data):
        request = self.context['request']
        lab_profile = data.get('lab_profile') or getattr(self.instance, 'lab_profile', None)
        scheduled_date = data.get('scheduled_date') or getattr(self.instance, 'scheduled_date', None)
        scheduled_minute = self.round_to_minute(scheduled_date)
        if scheduled_minute and scheduled_minute.tzinfo:
            scheduled_minute_utc = scheduled_minute.astimezone(timezone.utc)
        else:
            scheduled_minute_utc = scheduled_minute
        print(f"Scheduled Minute: {scheduled_minute}")
        print(f"Scheduled Date: {scheduled_date}")

        if lab_profile and scheduled_date:
            # conflict = LabTest.objects.filter(
            #     lab_profile=lab_profile,
            #     scheduled_date=scheduled_date
            # )
            all_tests = LabTest.objects.filter(
                    lab_profile=lab_profile,
                    scheduled_date__date=scheduled_minute.date(),
                    scheduled_date__hour=scheduled_minute.hour,
                    scheduled_date__minute=scheduled_minute.minute)
            print("All tests at this minute:", list(all_tests.values('id', 'scheduled_date', 'status')))
            conflict = LabTest.objects.annotate(
            scheduled_minute=TruncMinute('scheduled_date')
                ).filter(
                    lab_profile=lab_profile,
                    scheduled_minute=scheduled_minute_utc
                    )
            
            # Exclude self if updating
            if self.instance:
                conflict = conflict.exclude(pk=self.instance.pk)
            # Only block if not cancelled
            conflict = conflict.exclude(status='CANCELLED')
            print("Conflicting queryset:", conflict.query)
            print("Conflicting count:", conflict.count())
            if conflict.exists():
                raise serializers.ValidationError(
                    {"scheduled_date": "This slot is already booked for this lab."}
                )

        if request.method == 'POST':  # Only restrict creation
            if request.user.role != 'patient':
                raise serializers.ValidationError("Only patients can book lab tests.")
        return data
    def get_patient_name(self, obj):
        user = getattr(obj.patient, 'user', None)
        if user:
            return f"{user.first_name} {user.last_name}".strip()
        return ""
    def get_lab_profile_name(self, obj):
        if obj.lab_profile:
            return obj.lab_profile.name
        return ""
    def get_lab_profile_code(self,obj):
        if obj.lab_profile:
            return obj.lab_profile.user.user_id
        return ""


class LabAvailabilitySerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(input_formats=['%I:%M %p', '%H:%M:%S', '%H:%M'])
    end_time = serializers.TimeField(input_formats=['%I:%M %p', '%H:%M:%S', '%H:%M'])
    class Meta:
        model = LabAvailability
        fields = ['id', 'lab', 'date','start_time','end_time','available', 'created_at']
        read_only_fields = ['id', 'created_at','lab']












# class TestTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestType
#         fields = ['id', 'lab_type', 'name']
#         extra_kwargs = {
#             'id': {'read_only': True}
#         }

# class LabProfileSerializer(serializers.ModelSerializer):
#     test_types = TestTypeSerializer(many=True)
#     lab_types = serializers.PrimaryKeyRelatedField(queryset=LabType.objects.all(), many=True)
#     # test_types = serializers.PrimaryKeyRelatedField(queryset=TestType.objects.all(), many=True)
#     class Meta:
#         model = LabProfile
#         fields = ['id', 'user', 'name', 'address', 'phone', 'home_sample_collection', 'lab_types', 'test_types', 'created_at']
#         read_only_fields = ['id', 'user', 'created_at']

#     def create(self, validated_data):
#         lab_types_data = validated_data.pop('lab_types', [])
#         test_types_data = validated_data.pop('test_types', [])
        
#         lab_profile = LabProfile.objects.create(**validated_data)
        
#         lab_profile.lab_types.set(lab_types_data)
        
#         # Add test types
#         for test_type_data in test_types_data:
#             lab_type = test_type_data.pop('lab_type')
#             test_type = TestType.objects.create(lab_type=lab_type, **test_type_data)
#             test_type.labs.add(lab_profile)

#         return lab_profile
# class LabProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LabProfile
#         fields = ['id', 'user', 'name', 'address', 'phone', 'home_sample_collection', 'created_at']
#         read_only_fields = ['id', 'user', 'created_at']



# class TestTypeSerializer(serializers.ModelSerializer):
#     lab_type_name = serializers.CharField(source='lab_type.name', read_only=True)

#     class Meta:
#         model = TestType
#         fields = ['id', 'lab_type', 'lab_type_name', 'name']

# class TestTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestType
#         fields = ['id', 'lab_type', 'name']
#         extra_kwargs = {
#             'id': {'read_only': True}
#         }

# class LabProfileSerializer(serializers.ModelSerializer):
#     test_types = TestTypeSerializer(many=True, write_only=True)  # Nested serializer for TestType
#     lab_types = serializers.PrimaryKeyRelatedField(queryset=LabType.objects.all(), many=True)

#     class Meta:
#         model = LabProfile
#         fields = ['id', 'user', 'name', 'address', 'phone', 'home_sample_collection', 'lab_types', 'test_types', 'created_at']
#         read_only_fields = ['id', 'user', 'created_at']

#     def create(self, validated_data):
#         test_types_data = validated_data.pop('test_types', [])
#         lab_profile = LabProfile.objects.create(**validated_data)

#         # Add test types
#         for test_type_data in test_types_data:
#             lab_type = test_type_data.pop('lab_type')
#             test_type = TestType.objects.create(lab_type=lab_type, **test_type_data)
#             test_type.labs.add(lab_profile)

#         return lab_profile
