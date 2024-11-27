from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from task.models import Task
from task.serializers import TaskSerializer, TaskDetailSerializer


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("priority", "is_completed", "finish_date")

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return TaskDetailSerializer
        return TaskSerializer

    def get_queryset(self):
        """Filter tasks if User is owner and in assignee list"""
        user = self.request.user
        return Task.objects.filter(Q(user=user) | Q(assignees=user))

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)
