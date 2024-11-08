from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, TokenRefreshSerializer
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

class TokenObtainPairViewCustom(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class TokenRefreshViewCustom(TokenRefreshView):
    serializer_class = TokenRefreshSerializer