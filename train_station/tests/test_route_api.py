from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import Route, Station
from train_station.serializers import RouteListSerializer, RouteDetailSerializer


ROUTE_URL = reverse("train_station:route-list")


def detail_url(route_id):
    return reverse("train_station:route-detail", args=(route_id,))


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


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_route_unauthorized(self):
        sample_route()

        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_route_unauthorized(self):
        route = sample_route()

        res = self.client.get(detail_url(route.id))

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list(res.data), list(serializer.data))

    def test_create_route_unauthorized(self):
        Station.objects.create(
            name="Source Station",
            latitude=40.2936427,
            longitude=41.2936427
        )
        Station.objects.create(
            name="Destination Station",
            latitude=33.2936427,
            longitude=42.2936427
        )
        payload = {
            "source_station": 1,
            "destination_station": 2,
            "distance": 405
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_route_unauthorized(self):
        route = sample_route()

        res = self.client.delete(detail_url(route.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_route_unauthorized(self):
        route = sample_route()

        res = self.client.post(detail_url(route.id), {
            "name": "Route2"
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_route_authorized(self):
        sample_route()

        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_route_authorized(self):
        route = sample_route()

        res = self.client.get(detail_url(route.id))

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(list(res.data), list(serializer.data))

    def test_create_route_forbidden(self):
        Station.objects.create(
            name="Source Station",
            latitude=40.2936427,
            longitude=41.2936427
        )
        Station.objects.create(
            name="Destination Station",
            latitude=33.2936427,
            longitude=42.2936427
        )
        payload = {
            "source_station": 1,
            "destination_station": 2,
            "distance": 405
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_forbidden(self):
        route = sample_route()

        res = self.client.delete(detail_url(route.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        route = sample_route()

        res = self.client.post(detail_url(route.id), {
            "name": "Route2"
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        Station.objects.create(
            name="Source Station",
            latitude=40.2936427,
            longitude=41.2936427
        )
        Station.objects.create(
            name="Destination Station",
            latitude=33.2936427,
            longitude=42.2936427
        )
        payload = {
            "source_station": 1,
            "destination_station": 2,
            "distance": 405
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_route(self):
        route = sample_route()

        res = self.client.delete(detail_url(route.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
