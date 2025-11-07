from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer
from .models import User

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny]) #Indicates that any user can access this view
def login(request):
    #Take the data from the request and convert it to a serializer object for validation
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        #Authenticate the user
        user = authenticate(
            #Search the user in the database by username 
            username=request.data.get('username'),
            #Take the password and encrypt it temporarily.
            #Compare it with the encrypted password in the database
            password=request.data.get('password')
        )
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        #If authentication fails, return an error response
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    #If the input data is not valid, returns error
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny]) #Indicates that any user can access this view
def register(request):
    #serializer take the JSON data sent in the request
    #It is then converted to a serializer object for validation.
    serializer = UserRegisterSerializer(data=request.data)   
    
    #If the condition it's true...
    if serializer.is_valid():
        #The serializer is saves and creates a new user instance.
        #Execute the "create" method in the UserRegisterSerializer class
        user = serializer.save()
        
        #generates the JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            #Get the user object and convert to JSON
            #Use the UserProfileSerializer because it includes only the necessary fields
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
        
    
    #If the validation fails, returns errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) #Indicates that the user must be authenticated
def profile(request):
    
    serializer = UserProfileSerializer(request.user)
    
    #Return the user data
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)