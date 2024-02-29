import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # Minimum 8 characters
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # At least one number
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        # At least one special character
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
