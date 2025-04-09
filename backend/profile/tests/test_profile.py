from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from profile.models import image_file_path, EmailConfirmationToken

User = get_user_model()


class AccountNotAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_create_with_email_and_password_only(self):
        payload = {"email": "emailtest@mail.com", "password": "StrongPassword1!"}
        url = reverse("profile:create")

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["message"], "User registered successfully.")

    def test_email_validation(self):
        url = reverse("profile:create")
        correct_user_payload = {"email": "emailtest@mail.com", "password": "testPassword1!"}
        self.client.post(url, correct_user_payload)

        test_cases = [
            ("", "This field may not be blank."),
            ("incorrect_email.com", "Enter a valid email address."),
            ("emailtest@mail.com", "User with this email address already exists."),
        ]

        for invalid_email, expected_error in test_cases:
            payload = {"email": invalid_email, "password": "testPassword1!"}
            response = self.client.post(url, payload)

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(
                str(response.data["message"]["email"][0]), expected_error
            ), f"Expected error message: {expected_error}"

    @patch("profile.tasks.send_email.delay")
    def test_email_activation_link_send_when_profile_created(self, mock_send_email):
        payload = {"email": "emailtest@mail.com", "password": "testPassword1!"}
        url = reverse("profile:create")
        response = self.client.post(url, payload)

        user = get_user_model().objects.get(email=payload["email"])
        token = user.tokens.first()

        mock_send_email.assert_called_once_with(user.email, token.id, user.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


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
        url = reverse("profile:profile-manage")

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_image_file_path(self):
        user = get_user_model().objects.get(email="user@test.com")
        filename = "test_image.jpg"
        path = image_file_path(user, filename)

        # Check the start of the path
        self.assertTrue(path.startswith("uploads/users/"))

    def test_email_verification(self):
        user = get_user_model().objects.get(email="user@test.com")
        token = EmailConfirmationToken.objects.create(user=user)

        url = reverse("profile:email-verification")
        activation_link = url + f"?token_id={token.id}&user_id={user.id}"
        result = self.client.get(activation_link)

        get_activated_user = get_user_model().objects.get(email="user@test.com")

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue(get_activated_user.email_is_verified)

    def test_email_already_verified(self):
        user = get_user_model().objects.get(email="user@test.com")
        user.email_is_verified = True
        token = EmailConfirmationToken.objects.create(user=user)
        url = reverse("profile:email-verification")
        activation_link = url + f"?token_id={token.id}&user_id={user.id}"

        result = self.client.get(activation_link)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue(user.email_is_verified)
