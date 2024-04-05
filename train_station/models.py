from django.db import models
from django.core.exceptions import ValidationError

from train_station_api_service import settings


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField(default=50)
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    class Meta:
        ordering = ["cargo_num"]

    def __str__(self) -> str:
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=18)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["latitude", "longitude"],
                name="unique station"
            )
        ]
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )
    distance = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_station", "destination_station"],
                name="unique route"
            )
        ]
        ordering = ("source_station__name",)

    @staticmethod
    def validate_route(source, destination, error_to_raise):
        if destination == source:
            raise error_to_raise(
                "Station cannot have the same destination station"
            )

    def clean(self) -> None:
        self.validate_route(
            self.source_station,
            self.destination_station,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Route, self).save(*args, **kwargs)

    @property
    def route_name(self) -> str:
        return f"{self.source_station} - {self.destination_station}"

    def __str__(self) -> str:
        return (f"{self.source_station} -"
                f" {self.destination_station}"
                f" ({self.distance} km)")


class Trip(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="trips"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="trips"
    )
    crew = models.ManyToManyField(Crew, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["route", "train"],
                name="unique trip"
            )
        ]
        ordering = ["departure_time"]

    def __str__(self) -> str:
        return f"{str(self.route)} {self.train.name} - {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.customer} - {self.created_at}"


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "cargo", "seat"],
                name="unique ticket"
            )
        ]
        ordering = ["cargo", "seat"]

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return (
            f"{str(self.trip)} (cargo: {self.cargo}, seat: {self.seat})"
        )
