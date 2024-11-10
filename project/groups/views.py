from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Group, RecommendedMission, GroupParticipant
from .serializers import GroupSerializer, RecommendedMissionSerializer, GroupParticipantSerializer
import random

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        code = request.data.get('code')
        
        if group.code != code:
            return Response({"error": "잘못된 코드입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if GroupParticipant.objects.filter(user=request.user, group=group).exists():
            return Response({"error": "이미 그룹에 참여하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)

        GroupParticipant.objects.create(user=request.user, group=group)
        return Response({"message": "그룹에 참여했습니다."}, status=status.HTTP_200_OK)

class RecommendedMissionViewSet(viewsets.ViewSet):
    def list(self, request):
        # 30개의 미션 중 무작위로 5개 선택
        missions = RecommendedMission.objects.all()
        random_missions = random.sample(list(missions), 5)
        serializer = RecommendedMissionSerializer(random_missions, many=True)
        return Response(serializer.data)
