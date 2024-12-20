from rest_framework import serializers
from .models import Group, RecommendedMission, GroupParticipant
from users.serializers import UserSerializer
from manito.serializers import ManitoMatchSerializer

class RecommendedMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedMission
        fields = ['id', 'text']

class GroupParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_leader = serializers.BooleanField(read_only=True)

    class Meta:
        model = GroupParticipant
        fields = ['id', 'user', 'joined_at', 'is_leader']

class GroupSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    participants = GroupParticipantSerializer(many=True, read_only=True, source='groupparticipant_set')
    matches = ManitoMatchSerializer(many=True, read_only=True, source='manitomatch_set')

    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'mission', 'participants', 'matches']