from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import Crew
from train_station.serializers import CrewSerializer


CREW_URL = reverse("train_station:crew-list")


def detail_url(crew_id):
    return reverse("train_station:crew-detail", args=(crew_id,))


class UnauthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_crew_unauthorized(self):
        Crew.objects.create(
            first_name="Jon",
            last_name="Smith"
        )

        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_crew_forbidden(self):
        Crew.objects.create(
            first_name="Jon",
            last_name="Smith"
        )

        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_crew_admin(self):
        Crew.objects.create(
            first_name="Jon",
            last_name="Smith"
        )

        res = self.client.get(CREW_URL)
        trips = Crew.objects.all()
        serializer = CrewSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_crew(self):
        res = self.client.post(CREW_URL, {
            "first_name": "Jon",
            "last_name": "Smith"
        })

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_crew(self):
        crew = Crew.objects.create(
            first_name="Jon",
            last_name="Smith"
        )

        res = self.client.delete(detail_url(crew.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
