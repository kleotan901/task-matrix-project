import os
import uuid

from django.conf import settings
from django.utils import timezone
from datetime import datetime

from django.core.files.base import ContentFile
from payment.bill_generator import to_csv_content

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    avatar_url = models.ImageField(upload_to=image_file_path, blank=True)
    email_is_verified = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    mobile_phone = models.CharField(max_length=16, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self) -> str:
        if not self.last_name:
            self.last_name = ""
        self.full_name = super().get_full_name()
        return self.full_name


class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tokens"
    )


class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class SubscriptionHistory(models.Model):
    SUBSCRIPTION = [
        ("base", "Base plan"),
        ("premium", "Premium plan"),
        ("profi", "Profi plan"),
    ]
    PRICES = {
        "base": 0.00,
        "premium": 399.00,
        "profi": 699.00,
    }
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_history",
    )
    bill = models.FileField(upload_to="uploads/bills", max_length=254, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    plan = models.CharField(
        max_length=50, choices=SUBSCRIPTION, blank=True, default=None, null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=False)

    def bill_file_name(self):
        directory = os.path.join("media", "uploads", "bills")
        os.makedirs(directory, exist_ok=True)
        file_name = f"bill_{self.user.id}_{datetime.now().strftime('%Y-%m-%d')}.csv"
        return file_name

    def save(self, *args, **kwargs):
        if self.plan in self.PRICES:
            self.price = self.PRICES[self.plan]
        else:
            self.price = None
        # Create the bill's file name
        file_name = self.bill_file_name()

        content = {
            "email": self.user.email,
            "date": self.payment_date,
            "plan": self.plan,
            "price": self.price,
            "status": self.status,
        }

        csv_content = to_csv_content(content)

        # Save the bill file to the FileField
        self.bill.save(file_name, ContentFile(csv_content), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.plan} at {self.payment_date}"
