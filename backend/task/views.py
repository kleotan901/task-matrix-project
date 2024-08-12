from django.utils import timezone
from django.utils.dateparse import parse_date
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from task.models import Task, Tag
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
    filterset_fields = ("priority", "is_completed", "deadline", "finish_date")

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return TaskDetailSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def filter_queryset(self, queryset):
        """Filter tasks by current user"""
        queryset = self.request.user.created_tasks
        """Retrieve tasks by date"""
        date_param = self.request.query_params.get("deadline")
        if date_param:
            date_dt = parse_date(
                date_param
            )  # Parse the date from the query parameter and return datetime.date
            if date_dt:
                # Filter tasks where deadline is on the given date as datime.date
                queryset = queryset.filter(deadline__date=date_dt)

        finish_date_param = self.request.query_params.get("finish_date")
        if finish_date_param:
            date_dt = parse_date(finish_date_param)
            if date_dt:
                queryset = queryset.filter(finish_date__date=date_dt)
        return super().filter_queryset(queryset)

    @extend_schema(
        description="""
                List tasks with optional filters.

                **Query Parameters:**

                - **deadline** (date): Filter tasks with a specific deadline (YYYY-MM-DD).
                - **finish_date** (date): Filter tasks with a specific finish date (YYYY-MM-DD).
                - **is_completed** (boolean): Filter tasks based on completion status (true or false).
                - **priority** (string): Filter tasks by priority.

                **Example:**
                To filter tasks by priority and completion status:
                ```
                GET /tasks/?priority=Urgent+but+Not+Important&is_completed=true&deadline=
                ```
                """
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)
