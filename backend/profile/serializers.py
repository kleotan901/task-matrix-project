from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password,
    ValidationError
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import serializers

from profile.models import EmailConfirmationToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "full_name")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise DRFValidationError(e.messages)
        return value

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "full_name", "avatar_url", "bio")

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserGoogleSerializer(serializers.ModelSerializer):
    verified_email = serializers.BooleanField(
        source="email_is_verified", read_only=False
    )

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "full_name",
            "avatar_url",
            "verified_email",
        )


class EmailConfirmationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfirmationToken
        fields = ("id", "user")


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        min_length=8,
        validators=[validate_password],
        write_only=True,
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "new_password", "confirm_password")

    def validate_password(self, value):
        try:

            validate_password(value)
        except ValidationError as e:
            raise DRFValidationError(e.messages)
        return value
