from rest_framework import viewsets, status
from .models import ManitoMatch, ManitoMessage
from .serializers import ManitoMessageSerializer, ManitoMatchSerializer
from groups.models import Group
from users.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import random

class ManitoMessageViewSet(viewsets.ModelViewSet):
    queryset = ManitoMessage.objects.all()
    serializer_class = ManitoMessageSerializer


class CreateManitoMatchView(APIView):
    def post(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
            users = list(User.objects.filter(led_groups=group))

            if len(users) < 2:
                return Response({"error": "Not enough users in the group to create pairs."},
                                status=status.HTTP_400_BAD_REQUEST)

            random.shuffle(users)
            receivers = users[1:] + users[:1]

            with transaction.atomic():
                matches = []
                for giver, receiver in zip(users, receivers):
                    match = ManitoMatch.objects.create(
                        group=group,
                        giver=giver,
                        receiver=receiver
                    )
                    matches.append(match)

            serializer = ManitoMatchSerializer(matches, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Group.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)