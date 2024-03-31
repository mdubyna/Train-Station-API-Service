from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_station.models import Order, Ticket
from train_station.serializers import OrderListSerializer
from train_station.tests.test_trip_api import sample_trip


ORDER_URL = reverse("train_station:order-list")


def sample_order(**kwargs) -> Order:
    order_data = {
        "customer": get_user_model().objects.create_user(
            email="user@user.com",
            password="user12345"
        ),
    }
    order_data.update(kwargs)
    return Order.objects.create(**order_data)


class UnauthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_order_unauthorized(self):
        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_create_order_without_tickets(self):
        res = self.client.post(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_tickets(self):
        trip = sample_trip()

        print(trip.id)
        payload = {
            "tickets": [{
                "cargo": 3,
                "seat": 30,
                "trip": 1
            }]
        }

        res = self.client.post(ORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_order_client_without_orders(self):
        sample_order()

        res = self.client.get(ORDER_URL)
        orders = Order.objects.filter(customer=self.user)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_list_order_client_with_orders(self):
        order = sample_order(customer=self.user)
        Ticket.objects.create(
            cargo=5,
            seat=25,
            trip=sample_trip(),
            order=order
        )

        res = self.client.get(ORDER_URL)
        orders = Order.objects.filter(customer=self.user)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
