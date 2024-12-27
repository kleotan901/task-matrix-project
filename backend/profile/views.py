from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import logout
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from profile.models import EmailConfirmationToken, User, PasswordReset
from profile.serializers import (
    UserDetailSerializer,
    UserSerializer,
    EmailConfirmationTokenSerializer,
    UserGoogleSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer,
    UserUpdateSerializer,
    UserAvatarChangeOrDeleteSerializer,
)

from profile.tasks import send_email, send_reset_password, create_payments
from profile.utils import split_full_name
from payment.stripe import create_checkout_session
from payment.models import Payment


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = EmailConfirmationToken.objects.create(user=user)
        send_email.delay(user.email, token.id, user.id)

        create_payments.delay(user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ManageUserView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    serializer_class = UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        if self.request.method == "PUT":
            return UserUpdateSerializer
        if self.request.method == "PATCH":
            return UserAvatarChangeOrDeleteSerializer
        return UserSerializer

    @extend_schema(
        description="Retrieve the authenticated user's details.",
        responses={200: UserDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update full name or/and password",
        request=UserUpdateSerializer,
        responses={200: UserUpdateSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Change or delete avatar",
        request=UserAvatarChangeOrDeleteSerializer,
        responses={200: UserAvatarChangeOrDeleteSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class SendEmailConfirmationView(viewsets.ViewSet):
    serializer_class = EmailConfirmationTokenSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        description="""
        Sends an email confirmation link to the user's email address if the email is not verified.
        """
    )
    def post(self, request, format=None):
        user = request.user
        if not user.email_is_verified:
            token = EmailConfirmationToken.objects.get_or_create(user=user)
            send_email.delay(user.email, token[0].id, user.id)
            return Response(
                {"message": "The activation link has been sent to your email!"},
                status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "This email has already been verified"}, status.HTTP_201_CREATED
        )

    @extend_schema(
        description="""
        The activation link. Verifies the user's email using a token and user_id provided in the request.
        """
    )
    def email_verification(self, request):
        token_id = request.GET.get("token_id")
        try:
            token = EmailConfirmationToken.objects.get(id=token_id)
            user = token.user
            if user.email_is_verified:
                return Response(
                    {"message": "This email has already been verified"},
                    status.HTTP_200_OK,
                )
            user.email_is_verified = True
            user.save()
            return Response(
                {"message": "Email has been successfully verified!"}, status.HTTP_200_OK
            )
        except EmailConfirmationToken.DoesNotExist:
            return Response(
                {"message": "Email not confirm"}, status.HTTP_400_BAD_REQUEST
            )


class GoogleUserProfile(APIView):
    serializer_class = UserGoogleSerializer

    @extend_schema(
        description="Google Sign-In.",
        request=UserGoogleSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        user_info = request.data
        email = user_info.get("email")
        full_name = user_info.get("full_name")
        if not email:
            return Response(
                {
                    "message": "Email is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            return Response(
              {"message": "Invalid email address"},
              status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or update user in DB
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "avatar_url": user_info.get("avatar_url"),
                "email_is_verified": user_info.get("verified_email"),
            },
        )
        
        split_full_name(user, full_name)
        
        # If user already exists, update the necessary fields
        if not created:
            user.full_name = full_name
            user.avatar_url = user_info.get("avatar_url")
            user.email_is_verified = user_info.get("verified_email")
            user.save()

        if not user.payment.exists():
            create_payments.delay(user.id)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        jwt_tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": jwt_tokens,
            },
            status=status.HTTP_200_OK,
        )


class LogoutApi(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"message": "Logged out!"},
            status=status.HTTP_200_OK,
        )


class RequestPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=email, token=token)
            reset.save()

            # Sending reset link via email
            send_reset_password.delay(email, token)

            return Response(
                {"success": "We have sent you a link to reset your password"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User with credentials not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_password = data["new_password"]
        confirm_password = data["confirm_password"]

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)

        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response({"error": "Invalid token"}, status=400)

        user = User.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data["new_password"])
            user.save()

            reset_obj.delete()

            return Response({"success": "Password updated"})
        else:
            return Response({"error": "No user found"}, status=404)
