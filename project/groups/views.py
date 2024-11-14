from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Group, RecommendedMission, GroupParticipant
from .serializers import GroupSerializer, RecommendedMissionSerializer, GroupParticipantSerializer
from django.shortcuts import get_object_or_404
import random

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="그룹생성/작업완료",
        operation_description="그룹을 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'group_leader'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='그룹명'),
                'group_leader': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹장 User ID'),
                'mission': openapi.Schema(type=openapi.TYPE_STRING, description='미션내용'),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='성공 여부'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='응답 메시지'),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹 ID'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='그룹명'),
                            'code': openapi.Schema(type=openapi.TYPE_STRING, description='그룹 코드'),
                            'group_leader': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹장 User ID'),
                                    'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='그룹장 닉네임'),
                                }
                            ),
                            'missions': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_OBJECT)
                            ),
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
            self.perform_create(serializer)
            response_data = {
                'status': 'success',
                'message': 'Group created successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="그룹상세/작업완료",
        operation_description="그룹을 상세를 확인합니다.",
        responses={
            200: GroupSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        self.permission_classes = [AllowAny]
        group = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):

        group = serializer.save(group_leader=self.request.user)
        GroupParticipant.objects.create(user=self.request.user, group=group)


class GroupJoinView(APIView):
    @swagger_auto_schema(
        operation_summary="그룹참여/작업완료",
        operation_description="그룹에 참여합니다.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='응답 메시지'),
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
    def post(self, request, code):
        self.permission_classes = [IsAuthenticated]
        group = get_object_or_404(Group, code=code)
        
        if GroupParticipant.objects.filter(user=request.user, group=group).exists():
            return Response({"error": "이미 그룹에 참여하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)

        GroupParticipant.objects.create(user=request.user, group=group)
        
        participants = GroupParticipant.objects.filter(group=group)
        participant_serializer = GroupParticipantSerializer(participants, many=True)
        
        return Response({
            "message": "그룹에 참여했습니다.",
            "participants": participant_serializer.data
        }, status=status.HTTP_200_OK)

class RecommendedMissionViewSet(viewsets.ViewSet):
    def list(self, request):
        self.permission_classes = [AllowAny]
        missions = RecommendedMission.objects.all()
        random_missions = random.sample(list(missions), 5)
        serializer = RecommendedMissionSerializer(random_missions, many=True)
        return Response(serializer.data)
    
class UserGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="유저 그룹 조회/작업완료",
        operation_description="유저의 그룹을 조회합니다",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer {JWT_TOKEN}',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹 ID'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='그룹명'),
                        'code': openapi.Schema(type=openapi.TYPE_STRING, description='그룹 코드'),
                        'group_leader': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='그룹장 User ID'),
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='그룹장 닉네임'),
                            }
                        ),
                        'missions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
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
    def get(self, request):
        self.permission_classes = [IsAuthenticated]
        user_groups = GroupParticipant.objects.filter(user=request.user).select_related('group')
        groups = [participant.group for participant in user_groups]
        
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
