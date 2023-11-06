from rest_framework  import serializers
from .models import User, Review, OneTimeCode

from rest_framework import serializers

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

            


    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)

        if password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)
    
class VerifyEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = OneTimeCode
        fields = ['otp', 'email']


class ResendVerifyEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = OneTimeCode
        fields = ['email']


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    interest = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email','phone_number', 'bio', 'interest', 'rating', 'profile_picture', 'last_seen', 'followers_count']

    def get_followers_count(self, obj):
        return obj.followers.count()
    

class ProfileSerializer(serializers.ModelSerializer):
    interest = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['username', 'bio', 'interest', 'rating', 'profile_picture']
        read_only_fields = ('username', 'interest', 'rating', 'profile_picture')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user', 'reviewed_user','content', 'rating', 'created_at']
        read_only_fields = ('user','reviewed_user')

    def create(self, validated_data):
        user = self.context.get('user')
        r_user = self.context.get('reviewed_user')
        return Review.objects.create(user=user,reviewed_user=r_user, **validated_data)
    


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'profile_picture']