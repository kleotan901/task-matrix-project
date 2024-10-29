from django.db import models

from profile.models import User, SubscriptionHistory


class Payment(models.Model):
    ENUM_STATUS = [("PENDING", "pending"), ("PAID", "paid"), ("EXPIRED", "expired")]
    SUBSCRIPTION_TYPE = [
        ("premium", "premium"),
        ("profi", "profi"),
    ]

    status = models.CharField(max_length=20, choices=ENUM_STATUS)
    payment_type = models.CharField(
        max_length=50, choices=SUBSCRIPTION_TYPE, blank=True, default=None, null=True
    )
    user = models.ForeignKey(
        User,
        related_name="payment",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=500)
