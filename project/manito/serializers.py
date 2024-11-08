from rest_framework import serializers
from .models import ManitoMessage

class ManitoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManitoMessage
        fields = ['id', 'match', 'hint', 'letter']
