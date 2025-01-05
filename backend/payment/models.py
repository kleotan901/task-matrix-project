from django.db import models
from django.conf import settings


class Payment(models.Model):
    ENUM_STATUS = [("PENDING", "pending"), ("PAID", "paid"), ("EXPIRED", "expired")]
    SUBSCRIPTION_TYPE = [
        ("base", "base"),
        ("premium", "premium"),
        ("profi", "profi"),
    ]

    status = models.CharField(max_length=20, choices=ENUM_STATUS)
    subscription_type = models.CharField(
        max_length=50, choices=SUBSCRIPTION_TYPE, blank=True, default=None, null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="plan_and_subscription",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_url = models.URLField(max_length=500, blank=True)
    session_id = models.CharField(max_length=500, blank=True)
    subscription_id = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=False)
