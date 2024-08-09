from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from account.models import image_file_path, EmailConfirmationToken
from account.serializers import UserDetailSerializer, UserSerializer
from account.tasks import send_email


class AccountNotAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_create_with_email_and_password_only(self):
        payload = {"email": "emailtest@mail.com", "password": "testpassword"}
        url = reverse("account:create")

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_email_required(self):
        payload = {"email": "", "password": "testpassword"}
        url = reverse("account:create")

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "This field may not be blank.")

    @patch("account.tasks.send_email.delay")
    def test_email_activation_link_send_when_profile_created(self, mock_send_email):
        payload = {"email": "emailtest@mail.com", "password": "testpassword"}
        url = reverse("account:create")
        response = self.client.post(url, payload)

        user = get_user_model().objects.get(email=payload["email"])
        token = user.tokens.all()[0]

        mock_send_email.assert_called_once_with(user.email, token.id, user.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mock_send_email.called, 1)


class AccountAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword",
            first_name="John",
            last_name="Smith",
            email_is_verified=False,
        )
        self.client.force_authenticate(user=user)

    def test_password_change(self):
        payload = {"email": "emailtest@mail.com", "password": "NEWpassword"}
        url = reverse("account:profile-manage")

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_image_file_path(self):
        user = get_user_model().objects.get(email="user@test.com")
        filename = "test_image.jpg"
        path = image_file_path(user, filename)

        # Check the start of the path
        self.assertTrue(path.startswith("uploads/users/"))

    def test_full_name(self):
        payload = {
            "email": "user@test.com",
            "first_name": "Bob",
            "last_name": "Snail",
        }
        url = reverse("account:profile-manage")
        self.client.patch(url, payload)

        user = get_user_model().objects.get(email="user@test.com")
        serializer = UserDetailSerializer(user)

        self.assertEqual(
            serializer.data["full_name"], f"{user.first_name} {user.last_name}"
        )

    def test_email_verification(self):
        user = get_user_model().objects.get(email="user@test.com")
        token = EmailConfirmationToken.objects.create(user=user)

        url = reverse("account:email-verification")
        activation_link = url + f"?token_id={token.id}&user_id={user.id}"
        result = self.client.get(activation_link)

        get_activated_user = get_user_model().objects.get(email="user@test.com")

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue(get_activated_user.email_is_verified)

    def test_email_already_verified(self):
        user = get_user_model().objects.get(email="user@test.com")
        user.email_is_verified = True
        token = EmailConfirmationToken.objects.create(user=user)
        url = reverse("account:email-verification")
        activation_link = url + f"?token_id={token.id}&user_id={user.id}"

        result = self.client.get(activation_link)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue(user.email_is_verified)