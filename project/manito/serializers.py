from rest_framework import serializers
from .models import ManitoMessage, ManitoMatch

class ManitoMessageSerializer(serializers.ModelSerializer):
    giver = serializers.ReadOnlyField(source='giver.username')
    receiver = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = ManitoMessage
        fields = ['id', 'match', 'hint', 'letter', 'giver', 'receiver']

class ManitoMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManitoMatch
        fields = ['id', 'group', 'giver', 'receiver']