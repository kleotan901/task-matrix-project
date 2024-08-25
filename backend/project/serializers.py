from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction

from project.models import Project
from task.models import Task
from task.serializers import TaskListSerializer

import logging

logger = logging.getLogger(__name__)


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(read_only=False, required=False, many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "user",
            "name",
            "tasks",
            "start_date",
            "finish_date",
            "assignees",
        ]


class ProjectDetailSerializer(ProjectSerializer):
    tasks = TaskListSerializer(read_only=False, required=False, many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "user",
            "name",
            "tasks",
            "start_date",
            "finish_date",
            "assignees",
            "description",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop("user_id")
            assignees = validated_data.pop("assignees", [])
            user = get_user_model().objects.get(id=user_data)
            tasks_data = validated_data.pop("tasks", [])
            project = Project.objects.create(user=user, **validated_data)

            for task_data in tasks_data:
                task_assignees = task_data.pop("assignees", [])
                task_instance = Task.objects.create(user=user, **task_data)
                for assignee in task_assignees:
                    task_instance.assignees.add(assignee)

                project.tasks.add(task_instance)

            for assignee in assignees:
                project.assignees.add(assignee)

        return project

    def update(self, instance, validated_data):
        assignees = validated_data.pop("assignees", [])
        tasks_data = validated_data.get("tasks", [])
        # Update project fields
        instance.user = validated_data.get("user", instance.user)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.finish_date = validated_data.get("finish_date", instance.finish_date)
        instance.save()

        # Clear existing project assignees
        instance.assignees.clear()
        # Re-add assignees
        for assignee in assignees:
            instance.assignees.add(assignee)

        # Maps for id->instance and id->data item.
        task_data_mapping = {data["id"]: data for data in tasks_data if data.get("id")}
        tasks_of_project = Task.objects.filter(project=instance)
        task_mapping = {task.id: task for task in tasks_of_project}

        # Perform creations and updates.
        tasks_list = []
        for valid_task_data in tasks_data:
            if valid_task_data.get("id") is None:
                new_task = Task(
                    user=instance.user,
                    project=instance,
                    title=valid_task_data.get("title"),
                    start_date=valid_task_data.get("start_date"),
                    priority=valid_task_data.get("priority"),
                    is_completed=valid_task_data.get("is_completed"),
                )
                new_task.save()
                tasks_list.append(new_task)

        for task_id, data in task_data_mapping.items():
            task = task_mapping.get(task_id, None)
            # Update existing task
            task.title = data.get("title", task.title)
            task.start_date = data.get("start_date", task.start_date)
            task.start_date = data.get("start_date", task.start_date)
            task.priority = data.get("priority", task.priority)
            task.is_completed = data.get("is_completed", task.is_completed)
            task.save()

            # Clear existing task assignees
            task.assignees.clear()
            # Re-add assignees
            task_assignees = data.get("assignees", [])
            for task_assignee in task_assignees:
                task.assignees.add(task_assignee)

            tasks_list.append(task)

        instance.tasks.set(tasks_list)

        return instance
