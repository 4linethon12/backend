from django.urls import path
from rest_framework.routers import DefaultRouter

from manito.views import CreateManitoMatchView
from .views import GroupJoinView, RecommendedMissionViewSet, UserGroupsView

router = DefaultRouter()
router.register(r'groups', GroupJoinView)
router.register(r'recommended-missions', RecommendedMissionViewSet, basename='recommended-missions')

urlpatterns = [
    path('<int:group_id>/create-matches/', CreateManitoMatchView.as_view(), name='create-manito-matches'),
    path('groups/<str:code>/join/', GroupJoinView.as_view(), name='group-join'),
    path('user/groups/', UserGroupsView.as_view(), name='user-groups'),
] + router.urls