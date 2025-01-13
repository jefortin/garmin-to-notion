from __future__ import annotations

from _distance import DistanceUnit
from _time import TimeUnit


class Pace:
    """
    Represents the time it takes to cover a specific unit of distance.
    """

    def __init__(self, value: float, time_unit: TimeUnit, distance_unit: DistanceUnit):
        self.__value = value
        self.__time_unit = time_unit
        self.__distance_unit = distance_unit

    def __str__(self) -> str:
        return f"{self.__value} {self.__time_unit.value} / {self.__distance_unit.value}"

    def convert_to(self, new_time_unit: TimeUnit, new_distance_unit: DistanceUnit, ) -> Pace:
        """
        Converts the pace to a new unit and returns the new value.
        """
        time_ratio = self.__time_unit.get_conversion_ratio(new_time_unit)
        distance_ratio = self.__distance_unit.get_conversion_ratio(new_distance_unit)
        return Pace(
            self.__value * time_ratio / distance_ratio,
            new_time_unit,
            new_distance_unit,
        )
