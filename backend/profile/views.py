from django.conf import settings
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import RedirectView
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import logout
from rest_framework.views import APIView

import logging

logger = logging.getLogger(__name__)

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from profile.models import EmailConfirmationToken, User
from profile.serializers import (
    UserDetailSerializer,
    UserListSerializer,
    UserSerializer,
    EmailConfirmationTokenSerializer,
    GoogleLoginSerializer,
)

from profile.tasks import send_email

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from dj_rest_auth.registration.views import SocialLoginView


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = EmailConfirmationToken.objects.create(user=user)
        send_email.delay(user.email, token.id, user.id)

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


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CALLBACK_URL_YOU_SET_ON_GOOGLE
    client_class = OAuth2Client
    permission_classes = [AllowAny]
    serializer_class = GoogleLoginSerializer

    def get_response(self):
        """
        Returns the authorization token and user data.
        """
        try:
            original_response = super().get_response()
            token = self.token
            data = {"token": token.key, "user": self.user}
            return Response(data)
        except OAuth2Error as e:
            return Response(
                {"error": "Failed to fetch user info from Google.", "details": str(e)},
                status=500,
            )

    def process_login(self):
        """
        Автоматический вход в систему.
        """
        self.user = self.serializer.validated_data["user"]
        self.token, created = TokenModel.objects.get_or_create(user=self.user)
        super().process_login()


class UserRedirectView(LoginRequiredMixin, RedirectView, APIView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get(self, request, *args, **kwargs):
        # Handle the OAuth2 callback logic here
        code = request.GET.get("code")
        if code:
            # Exchange the code for tokens and process login
            # Redirect to another page or handle the response
            return redirect("profile:profile-manage")  # Redirect to a success page
        return redirect("profile:profile-manage")


class GoogleLoginAPIView(APIView):
    def get(self, request, *args, **kwargs):
        client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]
        redirect_uri = settings.CALLBACK_URL_YOU_SET_ON_GOOGLE
        scope = settings.SCOPE
        response_type = "code"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?response_type={response_type}&client_id={client_id}"
            f"&redirect_uri={redirect_uri}&scope={scope}"
        )

        return redirect(auth_url)


class GoogleCallbackAPIView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Exchange code for access token from google
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"],
            "client_secret": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"][
                "secret"
            ],
            "redirect_uri": settings.CALLBACK_URL_YOU_SET_ON_GOOGLE,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if "access_token" not in token_json:
            return Response(
                {"error": "Failed to get access token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_json["access_token"]

        # Use the access token to get user info
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_params = {"access_token": access_token}
        user_info_r = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_r.json()

        # Create or update user in DB
        user, created = User.objects.get_or_create(
            email=user_info["email"],
            defaults={
                "first_name": user_info["given_name"],
                "last_name": user_info["family_name"],
                "avatar_url": user_info["picture"],
                "email_is_verified": user_info["verified_email"],
            },
        )

        # If user already exists, update the necessary fields
        if not created:
            user.first_name = user_info["given_name"]
            user.last_name = user_info["family_name"]
            user.avatar_url = user_info["picture"]
            user.email_is_verified = user_info["verified_email"]
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        jwt_tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {"user": UserSerializer(user).data, "tokens": jwt_tokens},
            status=status.HTTP_200_OK,
        )


class LogoutApi(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"message": "Logged out!"},
            status=status.HTTP_200_OK,
        )
