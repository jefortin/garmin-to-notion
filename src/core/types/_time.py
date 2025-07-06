from __future__ import annotations

from datetime import timedelta
from enum import Enum


class TimeUnit(Enum):
    HOUR = 'h'
    MINUTE = 'm'
    SECOND = 's'
    MILLISECOND = 'ms'

    __unit_in_seconds: dict[str, float] = {
        # How many seconds are in each unit.
        HOUR: 3600,
        MINUTE: 60,
        SECOND: 1,
        MILLISECOND: 0.001,
    }

    def get_conversion_ratio(self, new_time_unit: TimeUnit) -> float:
        """
        Returns the conversion ratio from the current unit to the provided unit.

        i.e. `X * current_time_unit.get_conversion_ratio = Y` where `X` is the value in the current unit and `Y` is the
        value in the other unit.
        """
        self.__unit_in_seconds: dict[str, float]  # Enum scrambles type hint without this line.
        return self.__unit_in_seconds[self.value] / self.__unit_in_seconds[new_time_unit.value]


class DurationFormat(Enum):
    Dynamic = 'HH?:MM?:SS'
    H_M_S = 'HH:MM:SS'
    M_S = 'MM:SS'
    S = 'S'
    S_Precise = 'S.MMMM'

    def format_duration(self, duration: Duration) -> str:
        match self:
            case DurationFormat.Dynamic:
                hours, remaining = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remaining, 60)
                seconds = int(seconds)

                result = ""
                if hours: result += f"{hours:02?}:"
                if minutes: result += f"{minutes:02?}:"
                result += f"{seconds:02}"

                return result

            case DurationFormat.H_M_S:
                hours, remaining = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remaining, 60)
                seconds = int(seconds)
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            case DurationFormat.M_S:
                minutes, seconds = divmod(duration.total_seconds(), 60)
                seconds = int(seconds)
                return f"{minutes:02}:{seconds:02}"

            case DurationFormat.S:
                seconds = int(duration.total_seconds())
                return f"{seconds}"

            case DurationFormat.S_Precise:
                return f"{round(duration.total_seconds(), ndigits=2):05.2f}"

            case _:
                raise ValueError(f"Unsupported duration format: {self}")


class Duration(timedelta):
    """
    Represents the duration of an activity.
    """

    @classmethod
    def from_seconds(cls, seconds: float) -> Duration:
        return cls(seconds=seconds)

    @classmethod
    def from_minutes(cls, minutes: float) -> Duration:
        return cls(minutes=minutes)

    def total_minutes(self) -> float:
        return self.total_seconds() / 60

    def total_hours(self) -> float:
        return self.total_seconds() / 3600

    def format(self, format: DurationFormat) -> str:
        return format.format_duration(self)
