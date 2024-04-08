from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class UnauthenticatedRegisterApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_register(self):
        res = self.client.get("/api/user/register/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
