from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="projects",
    )
    start_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="assignees_projects", blank=True
    )
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name
