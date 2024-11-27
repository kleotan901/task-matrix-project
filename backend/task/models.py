from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from project.models import Project


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Важливо і терміново", "Важливо і терміново"),
        ("Важливо, але не терміново", "Важливо, але не терміново"),
        ("Не важливо, але терміново", "Не важливо, але терміново"),
        ("Не важливо і не терміново", "Не важливо і не терміново"),
    ]

    STATUS_CHOICES = [
        ("completed", "completed"),
        ("in_process", "in_process"),
        ("overdue", "overdue"),
    ]
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, blank=True, default=None, null=True
    )

    title = models.CharField(max_length=255)
    project = models.ForeignKey(
        Project,
        related_name="tasks",
        on_delete=models.SET_NULL,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="created_tasks",
    )
    comments = models.TextField(max_length=500, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="tasks", blank=True
    )

    def __str__(self):
        return f"{self.title} - {self.finish_date}({self.priority})"

    @staticmethod
    def validate_date_fields(start_date, finish_date):
        if start_date is not None or finish_date is not None:
            if start_date > finish_date:
                raise ValidationError(
                    "Finish date cannot be earlier than the start date."
                )

    def clean(self):
        Task.validate_date_fields(self.start_date, self.finish_date)
