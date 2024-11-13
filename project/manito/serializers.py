from rest_framework import serializers
from .models import ManitoMessage, ManitoMatch

class ManitoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManitoMessage
        fields = ['id', 'match', 'hint', 'letter']

class ManitoMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManitoMatch
        fields = ['id', 'group', 'giver', 'receiver']