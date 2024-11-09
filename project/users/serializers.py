from datetime import datetime

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth.hashers import make_password
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        credentials = {
            'nickname': attrs.get('nickname'),
            'password': attrs.get('password')
        }

        if not credentials['nickname'] or not credentials['password']:
            raise serializers.ValidationError("닉네임 및 비밀번호는 필수사항입니다.")

        try:
            user = User.objects.get(nickname=credentials['nickname'])
        except User.DoesNotExist:
            raise serializers.ValidationError("일치하는 계정을 찾을 수 없습니다.")

        if not user.check_password(credentials['password']):
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        refresh = self.get_token(user)
        access = refresh.access_token

        # 토큰 만료 시간 계산
        access_expire = datetime.fromtimestamp(access.payload['exp']).strftime('%Y-%m-%d %H:%M:%S')
        refresh_expire = datetime.fromtimestamp(refresh.payload['exp']).strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'nickname': user.nickname,
            'access': {
                'token': str(access),
                'expires_at': access_expire
            },
            'refresh': {
                'token': str(refresh),
                'expires_at': refresh_expire
            }
        }

        return data

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