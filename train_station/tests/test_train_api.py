from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import TrainType, Train
from train_station.serializers import TrainListSerializer, TrainDetailSerializer


TRAIN_URL = reverse("train_station:train-list")


def detail_url(train_id):
    return reverse("train_station:train-detail", args=(train_id,))


def sample_train() -> Train:
    train_type = TrainType.objects.create(
        name="Train Type"
    )
    return Train.objects.create(
        name="Train",
        cargo_num=10,
        places_in_cargo=50,
        train_type=train_type
    )


class UnauthenticatedTrainApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_train_unauthorized(self):
        sample_train()

        res = self.client.get(TRAIN_URL)
        trains = Train.objects.all()
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_train_unauthorized(self):
        train = sample_train()

        res = self.client.get(detail_url(train.id))

        serializer = TrainDetailSerializer(train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_unauthorized(self):
        TrainType.objects.create(
            name="Train Type"
        )

        payload = {
            "name": "Train",
            "cargo_num": 10,
            "places_in_cargo": 50,
            "train_type": 1
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_train_unauthorized(self):
        train = sample_train()

        res = self.client.delete(detail_url(train.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_train_unauthorized(self):
        train = sample_train()

        res = self.client.post(detail_url(train.id), {
            "name": "Train2"
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_train_authorized(self):
        sample_train()

        res = self.client.get(TRAIN_URL)
        trains = Train.objects.all()
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_train_authorized(self):
        train = sample_train()

        res = self.client.get(detail_url(train.id))

        serializer = TrainDetailSerializer(train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        TrainType.objects.create(
            name="Train Type"
        )

        payload = {
            "name": "Train",
            "cargo_num": 10,
            "places_in_cargo": 50,
            "train_type": 1
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_train_forbidden(self):
        train = sample_train()

        res = self.client.delete(detail_url(train.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_train_forbidden(self):
        train = sample_train()

        res = self.client.post(detail_url(train.id), {
            "name": "Train2"
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train(self):
        TrainType.objects.create(
            name="Train Type"
        )

        payload = {
            "name": "Train",
            "cargo_num": 10,
            "places_in_cargo": 50,
            "train_type": 1
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_train(self):
        train = sample_train()

        res = self.client.delete(detail_url(train.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
