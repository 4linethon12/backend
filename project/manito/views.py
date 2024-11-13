from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    @swagger_auto_schema(
        operation_summary="마니또 매칭",
        operation_description="마니또를 랜덤으로 매칭합니다.",
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='고유 ID'),
                        'group': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹 ID'),
                        'giver': openapi.Schema(type=openapi.TYPE_INTEGER, description='Giver User ID'),
                        'receiver': openapi.Schema(type=openapi.TYPE_INTEGER, description='Receiver User ID')
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
                }
            )
        }
    )
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