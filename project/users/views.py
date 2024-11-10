import logging

from rest_framework import viewsets, status, serializers
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

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

class TokenRefreshViewCustom(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            if not request.data.get('refresh'):
                return Response(
                    {'error': 'refresh 토큰이 제공되지 않았습니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            error_detail = e.detail
            if isinstance(error_detail, dict) and 'non_field_errors' in error_detail:
                error_message = error_detail['non_field_errors'][0]
            else:
                error_message = str(error_detail)

            logger.error(f"Validation error: {error_message}")
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Server error during token refresh: {str(e)}")
            return Response(
                {'error': '서버 오류가 발생했습니다'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )