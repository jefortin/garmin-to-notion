from __future__ import annotations

from abc import abstractmethod, ABC
from collections.abc import Callable
from datetime import timedelta, datetime, timezone
from typing import Annotated, Generic, TypeVar, Any, Self

from pydantic import Field, model_validator
from pydantic.experimental.pipeline import validate_as
from pydantic_extra_types.timezone_name import TimeZoneName
from pytz import timezone as pytz_timezone

from src.core.notion import NotionColumnType
from src.core.types import (
    DistanceUnit,
    Distance,
    Pace,
    Speed,
    TimeUnit,
    Duration,
)
from ._models import BridgeModel

# region custom types

SpeedTimeUnit = Annotated[
    TimeUnit,
    validate_as(str)
    .transform(lambda speed_str: speed_str.split('/')[1])
    .str_strip()
    .validate_as(TimeUnit)
]
SpeedDistanceUnit = Annotated[
    DistanceUnit,
    validate_as(str)
    .transform(lambda speed_str: speed_str.split('/')[0])
    .str_strip()
    .validate_as(DistanceUnit)
]
PaceTimeUnit = Annotated[
    TimeUnit,
    validate_as(str)
    .transform(lambda speed_str: speed_str.split('/')[0])
    .str_strip()
    .validate_as(TimeUnit)
]
PaceDistanceUnit = Annotated[
    DistanceUnit,
    validate_as(str)
    .transform(lambda speed_str: speed_str.split('/')[1])
    .str_strip()
    .validate_as(DistanceUnit)
]
TimeZone = Annotated[
    timezone,
    validate_as(TimeZoneName)
    .transform(lambda timezone_name: pytz_timezone(timezone_name))
]

# endregion custom types

# region data fields

T = TypeVar('T')
TNumber = TypeVar('TNumber', int, float)


class SynchronizationPlan(BridgeModel):
    """
    High-level representation of the synchronization plan between a Garmin model and a Notion database.
    """

    notion_database_name: str
    synchronized_fields: list[SynchronizedField]


class SynchronizedField(BridgeModel):
    """
    Represents a field that is synchronized between the specified Garmin model and a Notion database.
    """

    garmin_field_name: str
    notion_column_name: str
    field_type: SynchronizedFieldType


class SynchronizedFieldType(ABC, BridgeModel, Generic[T]):
    """
    Represents a value type that can be synchronized between a Garmin model and a Notion database.
    The type defined which Notion column types it can be synchronized to and how the data should be transformed
    to fit those column types.
    The transformation is expected to receive the right parameter type, which should be validated prior to invoking
    the transformation function.
    """

    @abstractmethod
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[T], Any]]:
        """
        Returns a dictionary of Notion column types to functions that transform the data field value into a valid value
        for that column type.
        """
        ...


class IdField(SynchronizedFieldType[str]):
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[str], Any]]:
        return {
            NotionColumnType.UNIQUE_ID: lambda value: str(value),
        }


class NumberField(SynchronizedFieldType[TNumber]):
    precision: int = Field(..., alias='precision')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[TNumber], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: f"{float(value or 0):.{self.precision}f}",
            NotionColumnType.NUMBER: lambda value: round(float(value or 0), self.precision),
            NotionColumnType.RICH_TEXT: lambda value: f"{float(value or 0):.{self.precision}f}",
        }


class TextField(SynchronizedFieldType[str]):
    default: str = Field(..., alias='default')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[str], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: value or self.default,
            NotionColumnType.RICH_TEXT: lambda value: value or self.default,
            NotionColumnType.SELECT: lambda value: value or self.default,
        }


class TrueFalseField(SynchronizedFieldType[bool]):
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[bool], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: 'Yes' if value else 'No',
            NotionColumnType.CHECKBOX: lambda value: bool(value),
            NotionColumnType.SELECT: lambda value: 'Yes' if value else 'No',
            NotionColumnType.RICH_TEXT: lambda value: 'Yes' if value else 'No',
        }


class DateField(SynchronizedFieldType[datetime]):
    timezone: TimeZone = Field(..., validation_alias='timezone')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[datetime], Any]]:
        return {
            NotionColumnType.TITLE: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
            NotionColumnType.RICH_TEXT: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
            NotionColumnType.DATE: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
        }


class DistanceField(SynchronizedFieldType[Distance]):
    unit: DistanceUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Distance], Any]]:
        return {
            NotionColumnType.TITLE: lambda distance: str(distance.convert_to(self.unit)),
            NotionColumnType.RICH_TEXT: lambda distance: str(distance.convert_to(self.unit)),
            NotionColumnType.NUMBER: lambda distance: round(distance.convert_to(self.unit).value, 2),
        }


class DurationField(SynchronizedFieldType[Duration]):
    unit: TimeUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[timedelta], Any]]:
        return {
            NotionColumnType.TITLE: lambda duration: str(duration),
            NotionColumnType.RICH_TEXT: lambda duration: str(duration),
            NotionColumnType.SELECT: lambda duration: str(duration),
            NotionColumnType.NUMBER: lambda duration: self.__convert_time(duration),
        }

    def __convert_time(self, duration: Duration) -> float:
        return round(duration.total_seconds() * TimeUnit.SECOND.get_conversion_ratio(self.unit), 2)


class SpeedField(SynchronizedFieldType[Speed]):
    distance_unit: SpeedDistanceUnit = Field(..., validation_alias='unit')
    time_unit: SpeedTimeUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Speed], Any]]:
        return {
            NotionColumnType.TITLE: lambda speed: str(speed),
            NotionColumnType.RICH_TEXT: lambda speed: str(speed),
            NotionColumnType.NUMBER: lambda speed: round(speed.value, 2),
        }


class PaceField(SynchronizedFieldType[Pace]):
    time_unit: PaceTimeUnit = Field(..., validation_alias='unit')
    distance_unit: PaceDistanceUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Pace], Any]]:
        return {
            NotionColumnType.TITLE: lambda pace: str(pace.convert_to(self.distance_unit)),
            NotionColumnType.RICH_TEXT: lambda pace: str(pace.convert_to(self.distance_unit)),
            NotionColumnType.NUMBER: lambda pace: round(pace.convert_to(self.distance_unit).value, 2),
        }

# endregion data fields
