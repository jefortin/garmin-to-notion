from __future__ import annotations

from _distance import DistanceUnit
from _time import TimeUnit


class Speed:
    """
    Represents the distance travelled over a specific unit of time.
    """

    def __init__(self, value: float, distance_unit: DistanceUnit, time_unit: TimeUnit):
        self.__value = value
        self.__distance_unit = distance_unit
        self.__time_unit = time_unit

    def __str__(self) -> str:
        return f"{self.__value} {self.__distance_unit.value} / {self.__time_unit.value}"

    def convert_to(self, new_distance_unit: DistanceUnit, new_time_unit: TimeUnit) -> Speed:
        """
        Converts the pace to a new unit and returns the new value.
        """
        distance_ratio = self.__distance_unit.get_conversion_ratio(new_distance_unit)
        time_ratio = self.__time_unit.get_conversion_ratio(new_time_unit)
        return Speed(
            self.__value * distance_ratio / time_ratio,
            new_distance_unit,
            new_time_unit,
        )
