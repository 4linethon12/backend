from rest_framework import viewsets
from .models import ManitoMatch, ManitoMessage
from .serializers import ManitoMessageSerializer
from groups.models import Group
from users.models import User

class ManitoMessageViewSet(viewsets.ModelViewSet):
    queryset = ManitoMessage.objects.all()
    serializer_class = ManitoMessageSerializer