from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import (
    Station,
    Station,
    Route,
    Station,
    Crew,
)
from train_station.serializers import StationSerializer

STATION_URL = reverse("train_station:station-list")


def detail_url(station_id):
    return reverse("train_station:station-detail", args=(station_id,))


class UnauthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_station_unauthorized(self):
        Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.get(STATION_URL)
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_station_unauthorized(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.get(detail_url(station.id))
        serializer = StationSerializer(station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list(res.data), list(serializer.data))

    def test_create_station_unauthorized(self):
        payload = {
            "name": "Kyiv",
            "latitude": 50.658798789,
            "longitude": 40.9806687989,
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_station_unauthorized(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.delete(detail_url(station.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_station_unauthorized(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.post(detail_url(station.id), {
            "name": "Lviv"
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_station_authorized(self):
        Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.get(STATION_URL)
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_station_authorized(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.get(detail_url(station.id))

        serializer = StationSerializer(station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list(res.data), list(serializer.data))

    def test_create_station_forbidden(self):
        payload = {
            "name": "Kyiv",
            "latitude": 50.658798789,
            "longitude": 40.9806687989,
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_station_forbidden(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.delete(detail_url(station.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_station_forbidden(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.post(detail_url(station.id), {
            "name": "Lviv"
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        payload = {
            "name": "Kyiv",
            "latitude": 50.658798789,
            "longitude": 40.9806687989,
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_station(self):
        station = Station.objects.create(
            name="Kyiv",
            latitude=50.658798789,
            longitude=40.9806687989,
        )

        res = self.client.delete(detail_url(station.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
