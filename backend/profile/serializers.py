from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from profile.models import EmailConfirmationToken, SubscriptionHistory
from profile.utils import split_full_name
from project.models import Project
from task.models import Task
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PlanAndSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = ("id", "user", "subscription_type", "price")


class SubscriptionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = ("id", "user", "bill", "payment_date", "plan")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "full_name")
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8}
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as error:
            raise DRFValidationError(error.messages)
        return value

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        full_name = validated_data.get("full_name", None)
        user = get_user_model().objects.create_user(**validated_data)
        if full_name:
            split_full_name(user, full_name)
        user.save()

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    # full_name = serializers.CharField(source="get_full_name", read_only=True)
    plan_and_subscription = PaymentSerializer(read_only=True, many=True)
    subscription_history = SubscriptionHistorySerializer(read_only=True, many=True)
    projects_number = serializers.SerializerMethodField()
    tasks_number = serializers.SerializerMethodField()
    couch_calls_number = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "projects_number",
            "tasks_number",
            "couch_calls_number",
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_phone",
            "avatar_url",
            "plan_and_subscription",
            "subscription_history",
        )

    def get_projects_number(self, obj) -> int:
        count_projects = Project.objects.filter(user=obj).count()
        return count_projects

    def get_tasks_number(self, obj) -> int:
        tasks_number = Task.objects.filter(user=obj).count()
        return tasks_number

    def get_couch_calls_number(self, obj) -> int:
        couch_calls_number = 0  # TODO
        return couch_calls_number


class UserUpdateSerializer(UserSerializer):
    email = serializers.CharField(read_only=True)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )
    plan_and_subscription = serializers.CharField(required=False)

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
            "plan_and_subscription",
        )

    def validate_current_password(self, value):
        user = self.context.get("request").user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your old password was entered incorrectly. Please try again."
            )

        return value

    def update(self, instance, validated_data):
        """Update a user's data"""
        current_password = validated_data.pop("current_password", None)
        new_password = validated_data.pop("new_password", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)
        mobile_phone = validated_data.pop("mobile_phone", None)
        plan_and_subscription = validated_data.pop("plan_and_subscription", None)

        instance.first_name = first_name
        instance.last_name = last_name
        instance.mobile_phone = mobile_phone
        if current_password:
            if new_password:
                instance.set_password(new_password)
        if plan_and_subscription:
            previous_record = (
                SubscriptionHistory.objects.filter(user=instance)
                .order_by("-payment_date")
                .first()
            )
            if previous_record:
                previous_record.status = False
                previous_record.save()

            new_record = SubscriptionHistory.objects.create(
                user=instance, subscription_type=plan_and_subscription, status=True
            )
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


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["full_name"] = self.user.full_name
        return data
