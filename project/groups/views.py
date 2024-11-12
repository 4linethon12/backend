from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Group, RecommendedMission, GroupParticipant
from .serializers import GroupSerializer, RecommendedMissionSerializer, GroupParticipantSerializer
from django.shortcuts import get_object_or_404
import random

class GroupJoinView(APIView):
    def post(self, request, code):
        group = get_object_or_404(Group, code=code)
        
        if GroupParticipant.objects.filter(user=request.user, group=group).exists():
            return Response({"error": "이미 그룹에 참여하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)

        GroupParticipant.objects.create(user=request.user, group=group)
        
        participants = GroupParticipant.objects.filter(group=group)
        participant_serializer = GroupParticipantSerializer(participants, many=True)
        
        return Response({
            "message": "그룹에 참여했습니다.",
            "participants": participant_serializer.data
        }, status=status.HTTP_200_OK)

class RecommendedMissionViewSet(viewsets.ViewSet):
    def list(self, request):

        missions = RecommendedMission.objects.all()
        random_missions = random.sample(list(missions), 5)
        serializer = RecommendedMissionSerializer(random_missions, many=True)
        return Response(serializer.data)
