from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

from project.models import Project
from project.serializers import ProjectSerializer, ProjectDetailSerializer
from task.models import Task

PROJECTS_URL = reverse("project:project-list")


def detail_url(project_id):
    return reverse("project:project-detail", args=[project_id])


def sample_user(**params):
    defaults = {"email": "emailtest@mail.com", "password": "testpassword"}
    defaults.update(params)

    return get_user_model().objects.create(**defaults)


def sample_project(**params):
    defaults = {
        "name": "Sample Project",
        "start_date": "2024-03-25",
        "finish_date": "2024-04-30",
        "description": "Sample description",
    }
    defaults.update(params)

    return Project.objects.create(**defaults)


class ProjectNotAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_task_list(self):
        response = self.client.get(PROJECTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Bob@mail.com", password="testpass123"
        )
        self.current_user = get_user_model().objects.create_user(
            email="Johnny@mail.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.current_user)

    def test_current_user_saved_as_project_owner(self):
        sample_project(user=self.user, name="Private Bob's Project 1")
        sample_project(user=self.user, name="Private Bob's Project 2")

        payload = {
            "user": self.current_user.id,
            "name": "Private Johnny's Project",
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "tasks": [],
            "assignees": [],
        }

        response = self.client.post(PROJECTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Get all projects from DB
        project_list_all = Project.objects.all()
        # Get projects where user_2 is assignee
        current_user_projects = project_list_all.filter(user=self.current_user)
        serializer = ProjectSerializer(current_user_projects, many=True)

        self.assertEqual(len(project_list_all), 3)
        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(serializer.data[0]["name"], "Private Johnny's Project")

    def test_creat_task_with_assignees_while_project_creating(self):
        payload = {
            "user": self.current_user.id,
            "name": "Private Johnny's Project",
            "tasks": [],
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "assignees": [self.user.id],
            "description": " ",
        }

        response = self.client.post(PROJECTS_URL, payload)

        serializer = ProjectDetailSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        project_instance = Project.objects.get(id=response.data["id"])

        task = Task.objects.create(
            user=self.current_user,
            title="First TestTask",
            project=project_instance,
            priority="Важливо, але не терміново",
        )
        task.assignees.add(self.user.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(serializer.is_valid())
        # Get all project from DB
        project_from_db = Project.objects.get(id=1)
        serializer = ProjectDetailSerializer(project_from_db)

        self.assertEqual(serializer.data["name"], "Private Johnny's Project")
        self.assertEqual(serializer.data["assignees"], [self.user.id])
        self.assertEqual(serializer.data["tasks"][0]["title"], "First TestTask")
        self.assertEqual(
            serializer.data["tasks"][0]["priority"], "Важливо, але не терміново"
        )
        self.assertEqual(serializer.data["tasks"][0]["assignees"], [1])

    def test_get_only_assignee_projects(self):
        user_1 = get_user_model().objects.get(email="Bob@mail.com")
        user_2 = get_user_model().objects.get(email="Johnny@mail.com")

        sample_project(user=user_1, name="Private TestProject")
        project_1 = sample_project(
            user=user_1,
            name="Delegated TestProject",
            description="Project delegated to Johnny",
        )
        project_1.assignees.add(user_2)

        response = self.client.get(PROJECTS_URL)
        # Get all projects from DB
        project_list_all = Project.objects.all()
        # Get projects where user_2 is assignee
        user_2_is_assignee_projects = project_list_all.filter(assignees__in=[user_2.id])
        serializer = ProjectSerializer(user_2_is_assignee_projects, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(serializer.data), 1)

    def test_update_project_with_assignees(self):
        project = sample_project(user=self.current_user)

        payload = {
            "name": "Updated project",
            "assignees": [self.user.id, self.current_user.id],
        }
        project_url = detail_url(project.id)
        response = self.client.put(project_url, payload)

        project_instance = Project.objects.get(id=project.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["assignees"],
            [assignee.id for assignee in project_instance.assignees.all()],
        )

    def test_create_task_with_assignees_while_project_updating(self):
        project = sample_project(user=self.current_user)
        task_payload = {
            "user": self.current_user.id,
            "title": "new task",
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "priority": "Важливо, але не терміново",
            "is_completed": False,
        }
        payload = {
            "user": self.current_user.id,
            "name": "Updated project",
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "tasks": [task_payload],
            "assignees": [],
            "description": " ",
        }

        serializer = ProjectDetailSerializer(project, data=payload)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        project_url = detail_url(project.id)
        response = self.client.put(project_url, payload)

        # Fetch the updated project instance and add task
        project_instance = Project.objects.get(id=project.id)
        task_payload.pop("user")
        task = Task.objects.create(
            user=self.current_user, project=project_instance, **task_payload
        )
        project_instance.tasks.add(task)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project_instance.name, payload["name"])
        self.assertIn(project_instance.tasks.all()[0].title, "new task")

    def test_update_tasks_in_project(self):
        project = sample_project(user=self.current_user)
        task = Task.objects.create(title="Test Task", project=project)

        task_payload_update = {
            "id": task.id,
            "user": self.current_user.id,
            "title": "Test Task Update",
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "priority": "Важливо, але не терміново",
            "is_completed": False,
        }
        payload = {
            "user": self.current_user.id,
            "name": "Updated project",
            "start_date": "2024-12-10",
            "finish_date": "2024-12-22",
            "tasks": [task_payload_update],
            "assignees": [],
            "description": " ",
        }

        serializer = ProjectDetailSerializer(project, data=payload)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        project_url = detail_url(project.id)
        response = self.client.put(project_url, serializer.data)

        # Fetch the updated project instance and updated task
        project_instance = Project.objects.get(id=project.id)
        task_db = Task.objects.get(id=task.id)
        project_instance.tasks.add(task_db)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project_instance.name, payload["name"])
        self.assertIn(project_instance.tasks.all()[0].title, "Test Task Update")
