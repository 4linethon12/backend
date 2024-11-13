from rest_framework.routers import DefaultRouter
from .views import ManitoMessageViewSet
from django.urls import path

router = DefaultRouter()
router.register(r'messages', ManitoMessageViewSet)

urlpatterns = [
    path('messages/group/<int:group_id>/', ManitoMessageViewSet.as_view({'get': 'list_by_group'}), name='group-messages')
] + router.urls