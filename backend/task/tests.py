from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

from project.models import Project
from task.models import Task
from task.serializers import TaskDetailSerializer, TaskSerializer

TASKS_URL = reverse("task:task-list")


def detail_url(task_id):
    return reverse("task:task-detail", args=[task_id])


def sample_user(**params):
    defaults = {"email": "Bob@mail.com", "password": "testpass123"}
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


def sample_task(**params):
    project = Project.objects.create(name="Test Project")
    defaults = {
        "title": "Sample task",
        "comments": "Sample description",
        "priority": "Важливо і терміново",
        "project": project,
    }
    defaults.update(params)
    return Task.objects.create(**defaults)


class TaskNotAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_task_list(self):
        response = self.client.get(TASKS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.current_user = sample_user(email="Johnny@mail.com", password="testpass123")
        self.client.force_authenticate(user=self.current_user)

    def test_get_task_list_serializer(self):
        project = Project.objects.create(name="Sample project")
        sample_task(user=self.current_user, project=project)
        sample_task(user=self.current_user, project=project)

        response = self.client.get(TASKS_URL)

        task_list = Task.objects.order_by("finish_date")
        serializer = TaskSerializer(task_list, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_task_with_assignees(self):
        project = Project.objects.create(name="Sample project")
        task = sample_task(title="Test Task 1", user=self.current_user)
        payload = {
            "title": "Updated task",
            "comments": "some info",
            "priority": "Важливо, але не терміново",
            "user": self.current_user,
            "start_date": "2024-12-12",
            "finish_date": "2024-12-12",
            "project": project,
            "assignees": [self.user.id],
        }
        url = reverse("task:task-detail", args=[task.id])
        response = self.client.put(url, payload)

        serializer = TaskDetailSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data["title"], "Updated task")
        self.assertEqual(serializer.data["assignees"], [1])

    def test_current_user_saved_as_task_owner(self):
        project = Project.objects.create(name="Sample project")
        payload = {
            "title": "new task",
            "comments": "some info",
            "priority": "Важливо, але не терміново",
            "user": self.current_user,
            "project": project,
        }

        response = self.client.post(TASKS_URL, payload)
        task = Task.objects.get(id=1)
        serializer = TaskSerializer(task)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_task_creation_with_assignees(self):
        project = Project.objects.create(name="Sample project")
        payload = {
            "title": "new task",
            "comments": "some info",
            "priority": "Важливо, але не терміново",
            "user": self.user,
            "assignees": [self.current_user.id],
            "project": project,
        }

        response = self.client.post(TASKS_URL, payload)
        serializer = TaskDetailSerializer(data=response.data)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        task = Task.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(task.assignees.all()[0].id, serializer.data["assignees"][0])
