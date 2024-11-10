from rest_framework import serializers
from .models import Group, RecommendedMission, GroupParticipant
from users.serializers import UserSerializer  

class GroupSerializer(serializers.ModelSerializer):
    group_leader = UserSerializer(read_only=True)
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'mission', 'group_leader']  

class RecommendedMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedMission
        fields = ['id', 'text']

class GroupParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupParticipant
        fields = ['id', 'user', 'joined_at']