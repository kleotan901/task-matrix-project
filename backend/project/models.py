from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


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

    @staticmethod
    def validate_date_fields(start_date, finish_date):
        if start_date is not None or finish_date is not None:
            if start_date > finish_date:
                raise ValidationError(
                    "Finish date cannot be earlier than the start date."
                )

    def clean(self):
        Project.validate_date_fields(self.start_date, self.finish_date)
