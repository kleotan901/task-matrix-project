from django.urls import path
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
        "email-confirmation/",
        SendEmailConfirmationView.as_view({"post": "post"}),
        name="email-confirmation",
    ),
    path(
        "email-verification/",
        SendEmailConfirmationView.as_view({"post": "email_verification"}),
        name="email-verification",
    ),
    path("login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("myprofile/", ManageUserView.as_view(), name="profile-manage"),
]
