from django.shortcuts import render
from django.shortcuts import get_object_or_404 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import UserSerializer
from .models import User

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny]) #Indicates that any user can access this view
def login(request):
    
    #Search in database the user with the username provided in the request
    #If the user does not exist, return a 404 error
    user = get_object_or_404(User, username=request.data.get('username'))
    
    #Check if the password provided mathces with the user´s password
    if not user.check_password(request.data.get('password')):
        #If not, return an error response
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    #Search if user already has a token
    #If exist (created=False), use it
    #If not (created=True), create a new one
    #"created" is a boolean
    token, created = Token.objects.get_or_create(user=user)
    
    #Convert the user object to JSON format
    #"(instance=user)" indicates that it is a serialization operation
    serializer = UserSerializer(instance=user)
    
    #Successful response
    return Response({'token': token.key,
                     'user': serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny]) #Indicates that any user can access this view
def register(request):
    #serializer take the JSON data sent in the request
    #It is then converted to a serializer object for validation.
    serializer = UserSerializer(data=request.data)   
    
    #If the condition it's true...
    if serializer.is_valid():
        #The serializer is saves and creates a new user instance.
        serializer.save()
        
        #Search in database the user who just was created
        user = User.objects.get(username=serializer.data['username'])
        #Encrypt the password and save the user
        user.set_password(request.data['password'])
        user.save()
        
        #Generate a unique token for the user
        token = Token.objects.create(user=user)
        #Successful response with token and user data
        return Response({'token': token.key,
                         'user': serializer.data},
                        status=status.HTTP_201_CREATED)
    
    #If the validation fails, returns errors
    return Response({serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated]) #Indicates that the user must be authenticated
def profile(request):
    
    #Serialize the authenticated user's data
    serializer = UserSerializer(instance=request.user)
    
    #Successful response with user data
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)