from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import EmailConfirmationToken
from account.serializers import (
    UserDetailSerializer,
    UserListSerializer,
    UserSerializer,
    EmailConfirmationTokenSerializer,
)
from account.tasks import send_email


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = EmailConfirmationToken.objects.create(user=user)
        send_email.delay(user.email, token.id, user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserSerializer

    @extend_schema(
        description="Retrieve the authenticated user's details.",
        responses={200: UserDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update the authenticated user's details and/or change the password.",
        request=UserSerializer,
        responses={200: UserSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Partially update the authenticated user's details.",
        request=UserListSerializer,
        responses={200: UserListSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


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
