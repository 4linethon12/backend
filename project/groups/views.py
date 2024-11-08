from rest_framework import viewsets, mixins
from .models import Group, RecommendedMission
from .serializers import GroupSerializer, RecommendedMissionSerializer
import random

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class RecommendedMissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RecommendedMissionSerializer

    def get_queryset(self):
        missions = list(RecommendedMission.objects.all())
        return random.sample(missions, 5) 
