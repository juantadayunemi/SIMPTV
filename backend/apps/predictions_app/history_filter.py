import re
import django_filters
from apps.traffic_app.models import Vehicle
from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import ExtractHour, TruncDate, TruncHour
from django.utils import timezone


class HistoryTrafficFilter(django_filters.FilterSet):
    congestion = django_filters.BooleanFilter(method="filter_congestion")
    velocity = django_filters.BooleanFilter(method="filter_velocity")
    volume = django_filters.BooleanFilter(method="filter_volume")

    location = django_filters.NumberFilter()
    date_from = django_filters.DateFilter()
    date_to = django_filters.DateFilter()

    class Meta:
        model = Vehicle
        fields = []

    def _filter_by_params(self, queryset):
        location = self.request.query_params.get("locationId")
        date_from = self.request.query_params.get("dateFrom")
        date_to = self.request.query_params.get("dateTo")

        if location and date_from and date_to:
            qs = queryset.filter(
                trafficAnalysisId__locationId=location,
                firstDetectedAt__range=[date_from, date_to],
            ).select_related("trafficAnalysisId")
            print("Filtered queryset:", qs)
            return qs

        return queryset

    def _days_analyzed(self, qs):
        return (
            qs.annotate(day=TruncDate("firstDetectedAt"))
            .values("day")
            .distinct()
            .count()
        )

    def _rush_hour(self, qs):
        tz = timezone.get_default_timezone()
        return (
            qs.annotate(hour=ExtractHour(TruncHour("firstDetectedAt", tzinfo=tz)))
            .values("hour")
            .annotate(count_vehicles=Count("id"))
            .order_by("-count_vehicles")
            .first()
        )

    def _vehicles_per_hour(self, qs):
        return (
            qs.annotate(hour=ExtractHour("firstDetectedAt"))
            .values("hour")
            .annotate(count_vehicles=Count("id"))
            .order_by("hour")
        )

    def _params_per_day(self, qs):
        return (
            qs.annotate(day=TruncDate("firstDetectedAt"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

    def _velocity_per_day(self, qs):
        return (
            qs.annotate(day=TruncDate("firstDetectedAt"))
            .values("day")
            .annotate(total=Avg("avgSpeed"))
            .order_by("day")
        )

    def filter_congestion(self, queryset, name, value):
        if value:

            PERMITTED_FREE_SPEED = 60  # Velocidad libre permitida en km/h
            qs = self._filter_by_params(queryset)
            if not qs.exists():
                return queryset
            avg_velocity = qs.aggregate(avg_velocity=Avg("avgSpeed"))["avg_velocity"]
            avg_congestion = 1 - (avg_velocity / PERMITTED_FREE_SPEED)

            self.congestion_result = {
                "avg_velocity": avg_velocity,
                "avg_congestion": avg_congestion,
                "rush_hour": self._rush_hour(qs),
                "days_analyzed": self._days_analyzed(qs),
                "congestion_per_day": self._params_per_day(qs),
            }
            return qs

        return queryset

    def filter_velocity(self, queryset, name, value):
        if value:

            qs = self._filter_by_params(queryset)
            if not qs.exists():
                return queryset

            avg_velocity = qs.aggregate(avg_velocity=Avg("avgSpeed"))["avg_velocity"]
            max_velocity = qs.aggregate(max_velocity=Max("avgSpeed"))["max_velocity"]
            min_velocity = qs.aggregate(min_velocity=Min("avgSpeed"))["min_velocity"]

            self.velocity_result = {
                "avg_velocity": avg_velocity,
                "max_velocity": max_velocity,
                "min_velocity": min_velocity,
                "days_analyzed": self._days_analyzed(qs),
                "velocity_per_day": self._velocity_per_day(qs),
            }
            return qs
        return queryset

    def filter_volume(self, queryset, name, value):
        if value:

            qs = self._filter_by_params(queryset)
            if not qs.exists():
                return queryset

            total_volume = qs.count()
            vehicle_per_hour = self._vehicles_per_hour(qs)

            avg_vehicles_per_hour = total_volume / (
                vehicle_per_hour.count() if vehicle_per_hour.count() > 0 else 1
            )

            self.volume_result = {
                "total_volume": total_volume,
                "avg_vehicles_per_hour": avg_vehicles_per_hour,
                "rush_hour": self._rush_hour(qs),
                "days_analyzed": self._days_analyzed(qs),
                "volume_per_day": self._params_per_day(qs),
            }
            return qs
        return queryset
