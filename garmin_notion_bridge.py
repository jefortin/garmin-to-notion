from abc import abstractmethod, ABC
from collections.abc import Callable
from datetime import timedelta, datetime, timezone
from typing import Annotated, Generic, TypeVar, Any

from pydantic import BaseModel, Field, AfterValidator
from pydantic.experimental.pipeline import validate_as
from pydantic_extra_types.timezone_name import TimeZoneName
from pytz import timezone as pytz_timezone

from _distance import DistanceUnit, Distance
from _fake_db import get_fake_db
from _garmin import GarminActivity
from _notion import NotionDatabase, NotionColumnType, NotionDatabaseColumn
from _pace import Pace
from _speed import Speed
from _time import TimeUnit


# region utilities

def check_is_valid_garmin_activity_field(field_name: str) -> None:
    garmin_activity_fields = GarminActivity.model_fields

    assert field_name in garmin_activity_fields, (
        f"Field '{field_name}' is not a valid Garmin activity field. "
        f"Available fields are: {', '.join(garmin_activity_fields.keys())}."
    )


# endregion utilities

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


class DataField(BaseModel, ABC, Generic[T]):
    garmin_activity_field: Annotated[
        str,
        AfterValidator(check_is_valid_garmin_activity_field)
    ]
    notion_column_name: str

    @abstractmethod
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[T], Any]]:
        """
        Returns a dictionary of Notion column types to functions that transform the data field value into a valid value
        for that column type.
        """
        ...


class NumberField(DataField[TNumber]):
    precision: int = Field(..., alias='precision')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[TNumber], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: f"{float(value):.{self.precision}f}",
            NotionColumnType.NUMBER: lambda value: round(float(value), self.precision),
            NotionColumnType.RICH_TEXT: lambda value: f"{float(value):.{self.precision}f}",
        }


class TextField(DataField[str]):
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[str], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: value,
            NotionColumnType.RICH_TEXT: lambda value: value,
            NotionColumnType.SELECT: lambda value: value,
        }


class TrueFalseField(DataField[bool]):
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[bool], Any]]:
        return {
            NotionColumnType.TITLE: lambda value: 'Yes' if value else 'No',
            NotionColumnType.CHECKBOX: lambda value: bool(value),
            NotionColumnType.SELECT: lambda value: 'Yes' if value else 'No',
            NotionColumnType.RICH_TEXT: lambda value: 'Yes' if value else 'No',
        }


class DateField(DataField[datetime]):
    timezone: TimeZone = Field(..., validation_alias='timezone')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[datetime], Any]]:
        return {
            NotionColumnType.TITLE: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
            NotionColumnType.RICH_TEXT: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
            NotionColumnType.DATE: lambda utcDate: utcDate.astimezone(self.timezone).strftime('%Y-%m-%d %H:%M'),
        }


class DistanceField(DataField[Distance]):
    unit: DistanceUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Distance], Any]]:
        return {
            NotionColumnType.TITLE: lambda distance: str(distance.convert_to(self.unit)),
            NotionColumnType.RICH_TEXT: lambda distance: str(distance.convert_to(self.unit)),
            NotionColumnType.NUMBER: lambda distance: round(distance.convert_to(self.unit).value, 2),
        }


class DurationField(DataField[timedelta]):
    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[timedelta], Any]]:
        return {
            NotionColumnType.TITLE: lambda duration: str(duration),
            NotionColumnType.RICH_TEXT: lambda duration: str(duration),
            NotionColumnType.SELECT: lambda duration: str(duration),
        }


class SpeedField(DataField[Speed]):
    distance_unit: SpeedDistanceUnit = Field(..., validation_alias='unit')
    time_unit: SpeedTimeUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Speed], Any]]:
        return {
            NotionColumnType.TITLE: lambda speed: str(speed),
            NotionColumnType.RICH_TEXT: lambda speed: str(speed),
            NotionColumnType.NUMBER: lambda speed: round(speed.value, 2),
        }


class PaceField(DataField[Pace]):
    time_unit: PaceTimeUnit = Field(..., validation_alias='unit')
    distance_unit: PaceDistanceUnit = Field(..., validation_alias='unit')

    def get_column_type_adapters(self) -> dict[NotionColumnType, Callable[[Pace], Any]]:
        return {
            NotionColumnType.TITLE: lambda pace: str(pace.convert_to(self.time_unit, self.distance_unit)),
            NotionColumnType.RICH_TEXT: lambda pace: str(pace.convert_to(self.time_unit, self.distance_unit)),
            NotionColumnType.NUMBER: lambda pace: round(pace.convert_to(self.time_unit, self.distance_unit).value, 2),
        }


# endregion data fields

# region schemas

class NotionColumnSchema(BaseModel):
    """
    Describes the expected schema of a Notion column.
    """
    name: str
    valid_types: list[NotionColumnType]


class NotionDatabaseSchema(BaseModel):
    """
    Describes the expected schema of a Notion database.
    """
    name: str
    columns: list[NotionColumnSchema]


class DatabaseValidationError(BaseModel):
    message: str


class DatabaseSchemaFactory:
    def create(self, database_title: str, data_fields: list[DataField]) -> NotionDatabaseSchema:
        return NotionDatabaseSchema(
            name=database_title,
            columns=[
                self.__get_schema_for_data_field(data_field)
                for data_field in data_fields
            ]
        )

    @staticmethod
    def __get_schema_for_data_field(data_field: DataField) -> NotionColumnSchema:
        return NotionColumnSchema(
            name=data_field.notion_column_name,
            valid_types=data_field.get_column_type_adapters().keys()
        )


# endregion schemas

class NotionDatabaseValidator:
    def validate_database(
        self,
        database: NotionDatabase,
        database_schema: NotionDatabaseSchema,
    ) -> list[DatabaseValidationError]:
        """
        Validates that a Notion database matches the expected schema.
        Returns a list of validation errors if the database does not match the schema.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """

        if validation_errors := self.__check_if_database_name_valid(database, database_schema):
            return [validation_errors]

        if validation_errors := self.__check_column_schemas_are_valid(database.properties, database_schema.columns):
            return validation_errors

        return []

    @staticmethod
    def __check_if_database_name_valid(
        database: NotionDatabase,
        database_schema: NotionDatabaseSchema,
    ) -> DatabaseValidationError | None:
        """
        Checks if the name of the database matches the expected name.
        Returns a validation error if the names do not match.
        """
        if database_schema.name not in database.names:
            return DatabaseValidationError(
                message=f"Database name '{database.name}' does not match the expected name '{database_schema.name}'."
            )

    @staticmethod
    def __check_column_schemas_are_valid(
        database_columns: list[NotionDatabaseColumn],
        column_schemas: list[NotionColumnSchema],
    ) -> list[DatabaseValidationError] | None:
        """
        Validates that the columns in the database match the expected schema.
        Returns a validation error for every missing column or invalid column.
        """
        validation_errors = []

        for column_schema in column_schemas:
            matching_column = next(
                (
                    column
                    for column in database_columns
                    if column.name == column_schema.name
                ),
                None,
            )

            if matching_column is None:
                validation_errors.append(
                    DatabaseValidationError(message=f"Column '{column_schema.name}' does not exist in the database.")
                )
                continue  # Further validation is not required since the column does not exist.

            if matching_column.type not in column_schema.valid_types:
                valid_type_list = ', '.join((valid_type.value for valid_type in column_schema.valid_types))
                validation_errors.append(
                    DatabaseValidationError(
                        message=(
                            f"Column '{column_schema.name}' is of type '{matching_column.type}', "
                            f"but should be one of: {valid_type_list}."
                        )
                    )
                )

        return validation_errors


if __name__ == '__main__':
    fields = [
        TextField.model_validate({
            'garmin_activity_field': 'id',
            'notion_column_name': 'ID',
        }),
        DistanceField.model_validate({
            'garmin_activity_field': 'distance',
            'notion_column_name': 'Distance (km)',
            'unit': 'km'
        }),
        DurationField.model_validate({
            'garmin_activity_field': 'duration',
            'notion_column_name': 'Duration (min)',
            'unit': 'm'
        }),
        NumberField.model_validate({
            'garmin_activity_field': 'calories',
            'notion_column_name': 'Calories',
            'precision': 0,
        }),
        PaceField.model_validate({
            'garmin_activity_field': 'average_pace',
            'notion_column_name': 'Avg Pace',
            'unit': 's/km'
        }),
        TextField.model_validate({
            'garmin_activity_field': 'training_effect',
            'notion_column_name': 'Training Effect',
        }),
        NumberField.model_validate({
            'garmin_activity_field': 'aerobic_score',
            'notion_column_name': 'Aerobic',
            'precision': 2,
        }),
        TextField.model_validate({
            'garmin_activity_field': 'aerobic_effect',
            'notion_column_name': 'Aerobic Effect',
        }),
        NumberField.model_validate({
            'garmin_activity_field': 'anaerobic_score',
            'notion_column_name': 'Anaerobic',
            'precision': 2,
        }),
        TextField.model_validate({
            'garmin_activity_field': 'anaerobic_effect',
            'notion_column_name': 'Anaerobic Effect',
        }),
        TrueFalseField.model_validate({
            'garmin_activity_field': 'is_personal_record',
            'notion_column_name': 'PR',
        }),
        TextField.model_validate({
            'garmin_activity_field': 'type',
            'notion_column_name': 'Activity Type',
        }),
        # SpeedField.model_validate({
        #     'garmin_activity_field': 'average_speed',
        #     'notion_column_name': 'Speed',
        #     'unit': 'km/h'
        # }),
    ]

    schema_factory = DatabaseSchemaFactory()
    database_schema = schema_factory.create('Activities', fields)

    database = NotionDatabase.model_validate(get_fake_db())

    validator = NotionDatabaseValidator()
    validation_errors = validator.validate_database(database, database_schema)

    if validation_errors:
        error_string = '\n'.join(error.message for error in validation_errors)
        print(f"Validation errors:\n{error_string}")

    assert 1
