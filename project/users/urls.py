from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet, LoginView, RegisterView, TokenRefreshViewCustom

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
] + router.urls
