from django.urls import path
from rest_framework.routers import DefaultRouter

from manito.views import CreateManitoMatchView
from .views import GroupViewSet, RecommendedMissionViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet)  # GroupViewSet의 엔드포인트
router.register(r'recommended-missions', RecommendedMissionViewSet, basename='recommended-missions')  # 추천 미션 엔드포인트

urlpatterns = [
    path('<int:group_id>/create-matches/', CreateManitoMatchView.as_view(), name='create-manito-matches'),
] + router.urls