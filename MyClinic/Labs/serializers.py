from rest_framework import serializers
from .models import LabTest, LabReport, LabProfile, LabType
from Patients.serializers import PatientProfileSerializer


class LabTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabType
        fields = ['id', 'name', 'tests', 'lab_profile']
        read_only_fields = ['id']

class LabProfileSerializer(serializers.ModelSerializer):
    lab_types = LabTypeSerializer(many=True, read_only=True)
    class Meta:
        model = LabProfile
        fields = ['id', 'user', 'name', 'lab_types','address', 'phone', 'home_sample_collection', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']




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


    class Meta:
        model = LabTest
        fields = ['id', 'patient','lab_profile', 'test_type', 'scheduled_date', 'registration_number' ,'status', 'created_at', 'reports']
    
    def validate(self, data):
        if self.context['request'].user.role != 'patient':
            raise serializers.ValidationError("Only patients can book lab tests.")
        return data















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
