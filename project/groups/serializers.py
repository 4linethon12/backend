from rest_framework import serializers
from .models import Group, RecommendedMission
from users.serializers import UserSerializer  

class GroupSerializer(serializers.ModelSerializer):
    group_leader = UserSerializer(read_only=True)  

    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'mission', 'group_leader']  

class RecommendedMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedMission
        fields = ['id', 'text']
