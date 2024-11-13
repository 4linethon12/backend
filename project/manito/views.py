from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import ManitoMatch, ManitoMessage
from .serializers import ManitoMessageSerializer, ManitoMatchSerializer
from groups.models import Group, GroupParticipant
from users.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import random

class ManitoMessageViewSet(viewsets.ModelViewSet):
    queryset = ManitoMessage.objects.all()
    serializer_class = ManitoMessageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="메세지 작성/작업완료",
        operation_description="마니또 메세지를 작성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=ManitoMessageSerializer,
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='성공 여부'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='응답 메시지'),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='메세지 ID'),
                            'match': openapi.Schema(type=openapi.TYPE_STRING, description='매칭 ID'),
                            'hint': openapi.Schema(type=openapi.TYPE_STRING, description='힌트'),
                            'letter': openapi.Schema(type=openapi.TYPE_STRING, description='내용'),
                        }
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            manito_message = serializer.save()
            response_data = {
                "status": "success",
                "message": "Message created successfully",
                "data": {
                    "id": manito_message.id,
                    "match": manito_message.match_id,
                    "hint": manito_message.hint,
                    "letter": manito_message.letter
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Bad request",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    @swagger_auto_schema(
        operation_summary="그룹별 메시지 조회",
        operation_description="특정 그룹의 모든 마니또 메시지를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'group_id',
                openapi.IN_PATH,
                description='메시지를 조회할 그룹 ID',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="성공적으로 그룹 메시지 조회 완료",
                schema=ManitoMessageSerializer(many=True)
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
                }
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='group/(?P<group_id>[^/.]+)')
    def list_by_group(self, request, group_id=None):
        # 특정 그룹의 메시지를 필터링
        messages = ManitoMessage.objects.filter(match__group_id=group_id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateManitoMatchView(APIView):
    @swagger_auto_schema(
        operation_summary="마니또 매칭/작업완료",
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
        self.permission_classes = [IsAuthenticated]
        try:
            group = Group.objects.get(id=group_id)
            users = list(User.objects.filter(id__in=GroupParticipant.objects.filter(group=group).values_list('user_id', flat=True)))

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