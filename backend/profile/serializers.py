from dj_rest_auth.registration.serializers import SocialLoginSerializer
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
            "first_name",
            "last_name",
            "role",
            "avatar_url",
            "bio",
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
        fields = ("id", "email", "first_name", "last_name", "avatar_url", "bio")


class UserDetailSerializer(UserListSerializer):
    @staticmethod
    def get_full_name(obj: User) -> str:
        return f"{obj.first_name} {obj.last_name}"

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "role",
            "avatar_url",
            "bio",
            "email_is_verified",
        )


class EmailConfirmationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfirmationToken
        fields = ("id", "user")


class GoogleLoginSerializer(SocialLoginSerializer):
    access_token = serializers.CharField(write_only=True)

    class Meta:
        fields = ("access_token",)
