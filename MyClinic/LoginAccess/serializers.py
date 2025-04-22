from rest_framework import serializers
from .models import User






class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'mobile_number',
            'password', 'password2', 'role']
        
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