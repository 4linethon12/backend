from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
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
    pagination_class = None

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
        match_id = request.data.get('match')

        match = get_object_or_404(ManitoMatch, id=match_id)

        if not match:
            return Response({"error": "유효하지 않은 match ID 입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.id != match.giver.id:
            return Response({"error": "giver만 메세지를 생성할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        match = ManitoMatch.objects.filter(id=match_id).first()
        if not match:
            return Response({"error": "유효하지 않은 match ID 입니다."}, status=status.HTTP_400_BAD_REQUEST)

        manito_message = ManitoMessage.objects.create(
            match=match,
            hint=request.data.get('hint', ''),
            letter=request.data.get('letter', ''),
        )

        response_data = {
            "status": "success",
            "message": "메세지가 성공적으로 생성되었습니다!",
            "data": {
                "id": manito_message.id,
                "match": manito_message.match_id,
                "hint": manito_message.hint,
                "letter": manito_message.letter,
                "giver": match.giver.id,
                "receiver": match.receiver.id,
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


    def perform_create(self, serializer):
        serializer.save()

    @swagger_auto_schema(
        operation_summary="그룹별 메시지 조회/작업",
        operation_description="특정 그룹의 모든 마니또 메시지를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'group_id',
                openapi.IN_PATH,
                description='메시지를 조회할 그룹 ID',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
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
    
    @swagger_auto_schema(
        operation_summary="Giver 입장에서 메시지 조회",
        operation_description="Giver가 receiver에게 작성한 메시지를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
    )
    @action(detail=False, methods=['get'], url_path='for-giver')
    def list_for_giver(self, request):
        match = ManitoMatch.objects.filter(giver=request.user)
        giver_messages = ManitoMessage.objects.filter(match__in=match)
        serializer = self.get_serializer(giver_messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Receiver 입장에서 메시지 조회",
        operation_description="Receiver가 giver로부터 받은 메시지를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'group_id',
                openapi.IN_PATH,
                description='메시지를 조회할 그룹 ID',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='for-receiver/(?P<group_id>[^/.]+)')
    def list_for_receiver(self, request, group_id=None):
        group = get_object_or_404(Group, id=group_id)
        participant = GroupParticipant.objects.filter(group=group, user=request.user)
        if not participant:
            return Response({"error": "그룹에 유저가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        match = ManitoMatch.objects.filter(group=group, receiver=request.user)
        receiver_messages = ManitoMessage.objects.filter(match__in=match)
        serializer = self.get_serializer(receiver_messages, many=True)
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