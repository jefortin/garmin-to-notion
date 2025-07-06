from __future__ import annotations

from ._distance import DistanceUnit
from ._time import TimeUnit, Duration, DurationFormat


class Pace:
    """
    Represents the time it takes to cover a specific unit of distance.
    """

    def __init__(self, value: float, time_unit: TimeUnit, distance_unit: DistanceUnit):
        self.__duration = Duration(seconds=value * time_unit.get_conversion_ratio(TimeUnit.SECOND))
        self.__distance_unit = distance_unit

    def __str__(self) -> str:
        return f"{self.__duration.format(DurationFormat.Dynamic)} / {self.__distance_unit.value}"

    def convert_to(self, new_distance_unit: DistanceUnit) -> Pace:
        """
        Converts the pace to a new unit and returns the new value.
        """
        distance_ratio = self.__distance_unit.get_conversion_ratio(new_distance_unit)
        return Pace(
            self.__duration.total_seconds() / distance_ratio,
            TimeUnit.SECOND,
            new_distance_unit,
        )
