from rest_framework.routers import DefaultRouter
from .views import ManitoMessageViewSet

router = DefaultRouter()
router.register(r'messages', ManitoMessageViewSet)  # 명확한 URL 패턴 지정

urlpatterns = router.urls
