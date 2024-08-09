from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from account.views import CreateUserView, ManageUserView, SendEmailConfirmationView

app_name = "account"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
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
    path("login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("myprofile/", ManageUserView.as_view(), name="profile-manage"),
]
