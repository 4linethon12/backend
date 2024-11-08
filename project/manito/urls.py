from rest_framework.routers import DefaultRouter
from .views import ManitoMessageViewSet

router = DefaultRouter()
router.register(r'', ManitoMessageViewSet)

urlpatterns = router.urls
