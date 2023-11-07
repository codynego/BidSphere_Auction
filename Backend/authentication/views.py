from django.shortcuts import render
from rest_framework.views import APIView, status
from .serializers import VerifyEmailSerializer, ResendVerifyEmailSerializer, RegistrationSerializer, VerifyEmailSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from userapp.models import User, Review
from rest_framework import authentication
from rest_framework import permissions
from userapp.tasks import send_activation_email
from userapp.utils import checkOTPExpiration
from userapp.models import OneTimeCode
#import get_or_404
from django.shortcuts import get_object_or_404
from userapp.utils import token_generator


from django.db import OperationalError

class RegistrationAPIView(generics.CreateAPIView):

    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                user_data = serializer.data
                user = User.objects.get(email=user_data['email'])

                send_email_task = send_activation_email.delay(username=user.username, email=user.email)

                if send_email_task.get() is False:
                    response_data = {
                        "message": "Error sending email!",
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                response_data = {
                    "message": "User registered successfully!",
                    "statusCode": status.HTTP_201_CREATED,
                    "data": user_data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except OperationalError as e:
            response_data = {
                "message": "Database connection error: " + str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            response_data = {
                "message": "An unexpected error occurred: " + str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            if OneTimeCode.objects.filter(otp=otp).exists():
                get_otp = OneTimeCode.objects.get(otp=otp)
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

