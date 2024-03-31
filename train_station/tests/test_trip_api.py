from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import (
    Train,
    TrainType,
    Station,
    Route,
    Trip,
    Crew,
)
from train_station.serializers import TripListSerializer, TripDetailSerializer


TRIP_URL = reverse("train_station:trip-list")
DEPARTURE_TIME = datetime.now()
ARRIVAL_TIME = datetime.now() + timedelta(hours=6)


def detail_url(trip_id):
    return reverse("train_station:trip-detail", args=(trip_id,))


def sample_route() -> Route:
    source_station = Station.objects.create(
        name="Source Station",
        latitude=40.2936427,
        longitude=41.2936427
    )
    destination_station = Station.objects.create(
        name="Destination Station",
        latitude=33.2936427,
        longitude=42.2936427
    )
    return Route.objects.create(
        source_station=source_station,
        destination_station=destination_station,
        distance=405
    )


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


def sample_trip(**kwargs) -> Trip:
    trip_data = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": DEPARTURE_TIME,
        "arrival_time": ARRIVAL_TIME
    }
    trip_data.update(kwargs)
    trip = Trip.objects.create(**trip_data)
    crew = Crew.objects.create(
            first_name="John",
            last_name="Smith"
        )
    trip.crew.add(crew)
    return trip


class UnauthenticatedTripApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_trip_unauthorized(self):
        sample_trip()

        res = self.client.get(TRIP_URL)
        trips = Trip.objects.all()
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
    
    def test_retrieve_trip_unauthorized(self):
        trip = sample_trip()

        res = self.client.get(detail_url(trip.id))

        serializer = TripDetailSerializer(trip)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_trip_unauthorized(self):
        sample_route()
        sample_train()
        Crew.objects.create(
            first_name="John",
            last_name="Smith"
        )
        payload = {
            "route": 1,
            "train": 1,
            "departure_time": DEPARTURE_TIME,
            "arrival_time": ARRIVAL_TIME,
            "crew": [1]
        }

        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_trip_unauthorized(self):
        trip = sample_trip()

        res = self.client.delete(detail_url(trip.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_trip_unauthorized(self):
        trip = sample_trip()

        res = self.client.post(detail_url(trip.id), {
            "arrival_time": datetime.now() + timedelta(days=1)
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_trip_authorized(self):
        sample_trip()

        res = self.client.get(TRIP_URL)
        trips = Trip.objects.all()
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_trip_authorized(self):
        trip = sample_trip()

        res = self.client.get(detail_url(trip.id))

        serializer = TripDetailSerializer(trip)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_trip_forbidden(self):
        sample_route()
        sample_train()
        Crew.objects.create(
            first_name="John",
            last_name="Smith"
        )
        payload = {
            "route": 1,
            "train": 1,
            "departure_time": DEPARTURE_TIME,
            "arrival_time": ARRIVAL_TIME,
            "crew": [1]
        }

        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_trip_forbidden(self):
        trip = sample_trip()

        res = self.client.delete(detail_url(trip.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_trip_forbidden(self):
        trip = sample_trip()

        res = self.client.post(detail_url(trip.id), {
            "arrival_time": datetime.now() + timedelta(days=1)
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTripTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_trip(self):
        sample_route()
        sample_train()
        Crew.objects.create(
            first_name="John",
            last_name="Smith"
        )
        payload = {
            "route": 1,
            "train": 1,
            "departure_time": DEPARTURE_TIME,
            "arrival_time": ARRIVAL_TIME,
            "crew": [1]
        }

        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_trip(self):
        trip = sample_trip()

        res = self.client.delete(detail_url(trip.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
