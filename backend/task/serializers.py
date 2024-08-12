from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction

from task.models import Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    tags = TagSerializer(many=True, required=False, read_only=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "start_date",
            "deadline",
            "finish_date",
            "description",
            "user",
            "priority",
            "tags",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user_id = validated_data.pop("user_id")
            task = Task.objects.create(user=user_id, **validated_data)
            if "tags" in validated_data:
                tags = validated_data.pop("tags")
                for tag in tags:
                    tag, created = Tag.objects.get_or_create(user_id=user_id, **tag)
                    task.tags.add(tag)
            return task


class TaskDetailSerializer(TaskSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "start_date",
            "deadline",
            "finish_date",
            "description",
            "user",
            "priority",
            "is_completed",
            "tags",
        ]
