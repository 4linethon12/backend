from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth.hashers import make_password
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'nickname'

    def validate(self, attrs):
        nickname = attrs.get("nickname")
        password = attrs.get("password")

        if not nickname or not password:
            raise serializers.ValidationError("닉네임 및 비밀번호는 필수사항입니다.")

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active account found with the given credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("No active account found with the given credentials")

        try:
            data = super().validate(attrs)
            data['nickname'] = user.nickname
            return data
        except Exception as e:
            print("Unexpected error during token generation:", e)
            raise serializers.ValidationError("An error occurred during login.")

class TokenRefreshSerializer(TokenRefreshSerializer):
    pass

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        print(validated_data['password'])
        return User.objects.create(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'created_at', 'updated_at']