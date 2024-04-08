from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from train_station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Trip,
    Order
)
from train_station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainDetailSerializer,
    StationSerializer,
    TrainListSerializer,
    RouteSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    CrewSerializer,
    TripSerializer,
    TripDetailSerializer,
    TripListSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminUser, )


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "retrieve":
            serializer = TrainDetailSerializer

        elif self.action == "list":
            serializer = TrainListSerializer

        return serializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source_station",
        "destination_station"
    )
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "retrieve":
            serializer = RouteDetailSerializer

        elif self.action == "list":
            serializer = RouteListSerializer

        return serializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


class TripViewSet(viewsets.ModelViewSet):
    queryset = (Trip.objects.select_related("train", "route")
                .prefetch_related("crew"))
    serializer_class = TripSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "retrieve":
            serializer = TripDetailSerializer

        elif self.action == "list":
            serializer = TripListSerializer

        return serializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "train__train_type",
                "route__source_station",
                "route__destination_station"
            ).prefetch_related("crew")

        return queryset


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__train",
        "tickets__trip__route",
        "tickets__trip__crew"
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
