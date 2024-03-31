from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import TrainType
from train_station.serializers import TrainTypeSerializer


TRAIN_TYPE_URL = reverse("train_station:traintype-list")


def detail_url(train_type_id):
    return reverse("train_station:traintype-detail", args=(train_type_id,))


class UnauthenticatedTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_train_type_unauthorized(self):
        TrainType.objects.create(
            name="test"
        )

        res = self.client.get(TRAIN_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="tests@tests.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_train_type_forbidden(self):
        TrainType.objects.create(
            name="tests"
        )

        res = self.client.get(TRAIN_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@tests.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_train_type_admin(self):
        TrainType.objects.create(
            name="tests"
        )

        res = self.client.get(TRAIN_TYPE_URL)
        trips = TrainType.objects.all()
        serializer = TrainTypeSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_train_type(self):
        res = self.client.post(TRAIN_TYPE_URL, {"name": "tests"})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_train_type(self):
        train_type = TrainType.objects.create(
            name="tests"
        )

        res = self.client.delete(detail_url(train_type.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
