from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from account.models import image_file_path
from account.serializers import UserDetailSerializer


class AccountCreateUserTestCase(TestCase):
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


class AccountAuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword",
            first_name="John",
            last_name="Smith",
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
