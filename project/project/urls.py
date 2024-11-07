from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # users 앱 URL 포함
    path('api/groups/', include('groups.urls')),  # groups 앱 URL 포함
]