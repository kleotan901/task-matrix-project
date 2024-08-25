from django.db.models import Q
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from project.models import Project
from project.serializers import ProjectSerializer, ProjectDetailSerializer


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ("update", "create", "partial_update"):
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_queryset(self):
        """Filter projects if User is owner and in assignee list"""
        user = self.request.user
        return Project.objects.filter(Q(user=user) | Q(assignees=user))
