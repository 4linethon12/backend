from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, TokenRefreshSerializer, RegisterSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="사용자 목록 조회",
        operation_description="모든 사용자의 정보를 조회합니다.",
        responses={
            200: UserSerializer(many=True),
            401: "인증되지 않은 사용자"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 상세 정보 조회",
        operation_description="특정 사용자의 상세 정보를 조회합니다.",
        responses={
            200: UserSerializer(),
            404: "사용자를 찾을 수 없음",
            401: "인증되지 않은 사용자"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="닉네임과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='사용자명'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호'),
            },
        ),
        responses={
            200: openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='액세스 토큰'),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='리프레시 토큰'),
                    }
                )
            ),
            400: "잘못된 요청"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Proceed with login if valid
            return Response(serializer.validated_data, status=200)
        else:
            # Print detailed errors if invalid
            print("Serializer validation errors:", serializer.errors)
            return Response({'detail': 'Invalid data provided', 'errors': serializer.errors}, status=400)

class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자를 등록합니다.",
        request_body=RegisterSerializer,
        responses={
            201: UserSerializer,
            400: "잘못된 요청"
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

class TokenRefreshViewCustom(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(
        operation_summary="토큰 갱신",
        operation_description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='리프레시 토큰'),
            },
        ),
        responses={
            200: openapi.Response(
                description="토큰 갱신 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='새로운 액세스 토큰'),
                    }
                )
            ),
            401: "유효하지 않은 토큰"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)