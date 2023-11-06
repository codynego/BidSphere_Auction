from django.shortcuts import render
from rest_framework.views import APIView, status
from .serializers import RegistrationSerializer, UserSerializer, ReviewSerializer, FollowSerializer, InterestSerializer, VerifyEmailSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import User, Review, Interest
from rest_framework import authentication
from rest_framework import permissions
from .tasks import send_activation_email
from .utils import checkOTPExpiration
from .models import OTP
#import get_or_404
from django.shortcuts import get_object_or_404
from .utils import token_generator

# Create your views here.

class RegistrationAPIView(generics.CreateAPIView):
    """
    This endpoint allows unauthenticated users to register new user.

    HTTP Methods:
        - POST: Create a new user.
    
    Request (POST):
        - JSON body: {
            "username": "username", 
            "email": "email", "password": "password"
        }

    Response (POST):
        - JSON body: {
            "message": "User registered successfully!",
            "statusCode": 201,
            "data": {
                "id": 1,
                "username": "username",
                "email": "email",
                "first_name": "",
                "last_name": "",

            }
    
    Authentication:
        - Authentication is not required.
    
    """
    serializer_class = RegistrationSerializer

    
    def post(self, request):
        """ Register new user."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "User registered successfully!",
                "statusCode": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            send_activation_email.delay(serializer.instance)
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailAPIView(generics.CreateAPIView):
    """
    This endpoint allows unauthenticated users to verify email.

    HTTP Methods:
        - POST: Verify email.

    Request (POST):
        - JSON body: {
            "otp": "otp", 
            "email": "email"
        }
    
    Response (POST):
        - JSON body: {
            "message": "User verified successfully!",
            "statusCode": 200,
        }

    Authentication:
        - Authentication is not required.
    """
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer =  self.serializer_class(data=data)

        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                response_data = {
                "message": "User does not exist! Please register.",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if OTP.objects.filter(otp=otp).exists():
                get_otp = OTP.objects.get(otp=otp)
            else:
                response_data = {
                "message": "Invalid OTP! Please try again.",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if checkOTPExpiration(get_otp):
                user.is_active = True
                user.is_verified = True
                user.save()
                get_otp.delete()
                response_data = {
                "message": "User verified successfully!",
                "statusCode": status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                get_otp.delete()
                response_data = {
                "message": "OTP expired!",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class ResendVerifyEmailAPIView(generics.CreateAPIView):
    """
    This endpoint allows unauthenticated users to resend verification email.

    HTTP Methods:
        - POST: Resend verification email.

    Request (POST):
        - JSON body: {
            "email": "email"
        }

    Response (POST):
        - JSON body: {
            "message": "OTP sent successfully!",
            "statusCode": 200,
        }

    Authentication:
        - Authentication is not required.
    """
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer =  self.serializer_class(data=data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = get_object_or_404(User, email=email)
            if user.is_verified:
                response_data = {
                "message": "User already verified!",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                send_activation_email.delay(user)
                response_data = {
                    "message": "OTP sent successfully!",
                    "statusCode": status.HTTP_200_OK,
                    }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

