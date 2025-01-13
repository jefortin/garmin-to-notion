from __future__ import annotations

from enum import Enum


class DistanceUnit(Enum):
    KILOMETER = 'km'
    METER = 'm'

    __unit_in_meters: dict[str, float] = {
        KILOMETER: 1000,
        METER: 1,
    }

    def get_conversion_ratio(self, new_distance_unit: DistanceUnit) -> float:
        """
        Returns the conversion ratio from the current unit to the provided unit.

        i.e. `X * conversion_ratio = Y` where `X` is the value in the current unit and `Y` is the value in the other
        unit.
        """
        self.__unit_in_meters: dict[str, float]  # Enum scrambles type hint without this line.
        return self.__unit_in_meters[self.value] / self.__unit_in_meters[new_distance_unit.value]


class Distance:
    """
    Represents a distance value with a specific unit.
    """

    def __init__(self, value: float, unit: DistanceUnit):
        self.__value = value
        self.__unit = unit

    def __str__(self) -> str:
        return f"{self.__value} {self.__unit.value}"

    def convert_to(self, new_distance_unit: DistanceUnit) -> Distance:
        """
        Converts the distance to a new unit and returns the new value.
        """
        return Distance(
            self.__value * self.__unit.get_conversion_ratio(new_distance_unit),
            new_distance_unit,
        )
