from django.contrib import admin

from train_station.models import (
    Train,
    TrainType,
    Crew,
    Station,
    Route,
    Trip,
    Order,
    Ticket
)


admin.site.register(TrainType)
admin.site.register(Crew)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("name", "cargo_num", "places_in_cargo", "train_type")
    list_filter = ("train_type__name",)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    ordering = ("latitude",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source_station", "destination_station", "distance")
    list_filter = ("source_station__name", "destination_station__name")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("route", "train", "departure_time", "arrival_time")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "customer")
    search_fields = ("customer",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("trip", "cargo", "seat", "order")
    search_fields = ("order",)
