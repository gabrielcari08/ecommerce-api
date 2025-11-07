from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    #"write_true=True" means that this field won´t be included in the response
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User #Convert User objects to JSON
        fields = ['username', 'email', 'password', 'password2', 'user_type']
        extra_kwargs = {
            'email': {'required': True}, #This field is necessary
        }
        
    #Validate that password fields match and that the email isn't registered yet.
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't matches"})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered"})
        
        return attrs
    
    #This method is executed when we call "serializer.save()". Also creates the object in the database. 
    def create(self, validated_data):
        #Delete the 'password2' field from data because this field is only to validation
        validated_data.pop('password2')
        #Create the user
        #Will use the "create_user" because encrypt the password automatically
        user = User.objects.create_user(**validated_data)
        #Return the user object created
        return user
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'date_joined']