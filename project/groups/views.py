from rest_framework import viewsets
from rest_framework.response import Response
from .models import Group, RecommendedMission
from .serializers import GroupSerializer, RecommendedMissionSerializer
import random

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class RecommendedMissionViewSet(viewsets.ViewSet):
    def list(self, request):
        # 30개의 미션 중 무작위로 5개 선택
        missions = Mission.objects.all()
        random_missions = random.sample(list(missions), 5)
        serializer = RecommendedMissionSerializer(random_missions, many=True)
        return Response(serializer.data)
