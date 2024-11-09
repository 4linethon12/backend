from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, RecommendedMissionViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet)  # GroupViewSet의 엔드포인트
router.register(r'recommended-missions', RecommendedMissionViewSet, basename='recommended-missions')  # 추천 미션 엔드포인트

urlpatterns = router.urls