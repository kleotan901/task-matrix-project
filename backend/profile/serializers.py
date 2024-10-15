from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import serializers, status
from rest_framework.response import Response

from profile.models import EmailConfirmationToken, SubscriptionHistory
from profile.utils import split_full_name


class PlanAndSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = ("id", "user", "subscription_type", "price")


class SubscriptionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = ("id", "user", "payment_date", "subscription_type", "price", "status")


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
        full_name = validated_data.pop("full_name", None)
        user = get_user_model().objects.create_user(**validated_data)
        if full_name:
            split_full_name(user, full_name)
        user.save()

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    # full_name = serializers.CharField(source="get_full_name", read_only=True)
    plan_and_subscription = serializers.SerializerMethodField()
    subscription_history = SubscriptionHistorySerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_phone",
            "avatar_url",
            "plan_and_subscription",
            "subscription_history",
        )

    def get_plan_and_subscription(self, obj):
        return [{plan: price} for plan, price in SubscriptionHistory.PRICES.items()]


class UserUpdateSerializer(UserSerializer):
    email = serializers.CharField(read_only=True)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile_phone",
            "current_password",
            "new_password",
        )

    def validate_current_password(self, value):
        user = self.context.get("request").user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your old password was entered incorrectly. Please try again."
            )

        return value

    def update(self, instance, validated_data):
        """Update a user's full name and/or change the password"""
        current_password = validated_data.pop("current_password", None)
        new_password = validated_data.pop("new_password", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)
        mobile_phone = validated_data.pop("mobile_phone", None)
        if first_name:
            instance.first_name = first_name
        if last_name:
            instance.last_name = last_name
        if current_password:
            if new_password:
                instance.set_password(new_password)
        if mobile_phone:
            instance.mobile_phone = mobile_phone
        instance.save()
        return super().update(instance, validated_data)


class UserAvatarChangeOrDeleteSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "avatar_url")

    def update(self, instance, validated_data):
        instance.avatar_url = validated_data.get("avatar_url")
        instance.save()
        return super().update(instance, validated_data)


class UserGoogleSerializer(serializers.ModelSerializer):
    verified_email = serializers.BooleanField(
        source="email_is_verified", read_only=False
    )
    full_name = serializers.CharField(source="get_full_name", read_only=True)

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
        except ValidationError as err:
            raise DRFValidationError(err.messages)
        return value
