from django.conf import settings
from django.db import models
from rest_framework.reverse import reverse


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, default=None)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Urgent and important", "Urgent and important"),
        ("Important but Not Urgent", "Important but Not Urgent"),
        ("Urgent but Not Important", "Urgent but Not Important"),
        ("Neither Urgent nor Important", "Neither Urgent nor Important"),
    ]

    STATUS_CHOICES = [
        ("completed", "completed"),
        ("in_process", "in_process"),
        ("overdue", "overdue"),
    ]
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )
    description = models.TextField(max_length=500, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="tasks")
    tags = models.ManyToManyField(Tag, related_name="tasks", default=None, blank=True)

    def __str__(self):
        return f"{self.title} {self.deadline}({self.priority})"
