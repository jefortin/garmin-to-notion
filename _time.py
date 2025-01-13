from __future__ import annotations

from enum import Enum


class TimeUnit(Enum):
    HOUR = 'h'
    MINUTE = 'm'
    SECOND = 's'
    MILLISECOND = 'ms'

    __unit_in_seconds: dict[TimeUnit, float] = {
        HOUR: 3600,
        MINUTE: 60,
        SECOND: 1,
        MILLISECOND: 0.001,
    }

    def get_conversion_ratio(self, new_time_unit: TimeUnit) -> float:
        """
        Returns the conversion ratio from the current unit to the provided unit.

        i.e. `X * conversion_ratio = Y` where `X` is the value in the current unit and `Y` is the value in the other
        unit.
        """
        self.__unit_in_seconds: dict[TimeUnit, float]  # Enum scrambles type hint without this line.
        return self.__unit_in_seconds[self] / self.__unit_in_seconds[new_time_unit]
