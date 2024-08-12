from django.conf import settings
from django.db import models
from rest_framework.reverse import reverse


class Tag(models.Model):
    name = models.CharField(max_length=64, default=None)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tags",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        unique_together = ("name", "user")

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Urgent and important", "Do First"),
        ("Important but Not Urgent", "Schedule"),
        ("Urgent but Not Important", "Delegate"),
        ("Neither Urgent nor Important", "Eliminate"),
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
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)

    def __str__(self):
        return f"{self.title} {self.deadline}({self.priority})"
