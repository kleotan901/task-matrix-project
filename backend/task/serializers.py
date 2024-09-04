from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from project.models import Project
from task.models import Task


class TaskListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    assignees = serializers.SlugRelatedField(
        slug_field="id",
        read_only=False,
        required=False,
        many=True,
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "title",
            "start_date",
            "finish_date",
            "assignees",
            "is_completed",
            "priority",
            "status",
        ]


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    project = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "title",
            "priority",
            "assignees",
            "start_date",
            "finish_date",
            "status",
            "comments",
            "is_completed",
            "project",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop("user_id")
            assignees = validated_data.pop("assignees", [])
            project = validated_data.pop("project")
            if project is None:
                raise ValidationError("Project field cannot be blank.")

            user = get_user_model().objects.get(id=user_data)
            task = Task.objects.create(user=user, **validated_data)
            for assignee in assignees:
                task.assignees.add(assignee)
        return task


class TaskDetailSerializer(TaskSerializer):
    project = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "priority",
            "assignees",
            "start_date",
            "finish_date",
            "comments",
            "user",
            "is_completed",
            "project",
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            assignees = validated_data.pop("assignees", [])
            instance.title = validated_data.get("title", instance.title)
            instance.priority = validated_data.get("priority", instance.priority)
            instance.comments = validated_data.get("comments", instance.comments)
            instance.start_date = validated_data.get("start_date", instance.start_date)
            instance.finish_date = validated_data.get(
                "finish_date", instance.finish_date
            )

            instance.project = validated_data.get("project", instance.project)
            instance.is_completed = validated_data.get(
                "is_completed", instance.is_completed
            )
            instance.save()

            instance.assignees.clear()
            for assignee in assignees:
                instance.assignees.add(assignee)

        return instance
