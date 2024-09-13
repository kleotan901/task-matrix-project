from django.contrib.auth import get_user_model
from rest_framework import serializers

from profile.models import User, EmailConfirmationToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "full_name"
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "full_name", "avatar_url", "bio")


class UserDetailSerializer(UserListSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "avatar_url",
            "bio",
            "email_is_verified",
        )


class UserGoogleSerializer(UserListSerializer):
    verified_email = serializers.BooleanField(source="email_is_verified", read_only=False)

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
