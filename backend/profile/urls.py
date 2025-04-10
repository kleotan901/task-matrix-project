from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from profile.views import (
    CreateUserView,
    ManageUserView,
    SendEmailConfirmationView,
    LogoutApi,
    GoogleUserProfile,
    RequestPasswordReset,
    ResetPassword,
)

from profile.views import LoginView

app_name = "profile"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("google/", GoogleUserProfile.as_view(), name="google"),
    path(
        "sent-email-verify/",
        SendEmailConfirmationView.as_view({"post": "post"}),
        name="sent-email-verify",
    ),
    path(
        "email-verification/",
        SendEmailConfirmationView.as_view({"get": "email_verification"}),
        name="email-verification",
    ),
    path("login/", LoginView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("myprofile/", ManageUserView.as_view(), name="profile-manage"),
    path("logout/", LogoutApi.as_view(), name="logout"),
    path("reset-password/", RequestPasswordReset.as_view(), name="reset-password"),
    path(
        "confirm-password/<str:token>/",
        ResetPassword.as_view(),
        name="confirm-password",
    ),
]
