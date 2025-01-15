from typing import Annotated, Literal

from pydantic import BaseModel, Field, AfterValidator, ValidationError
from pydantic.experimental.pipeline import validate_as

from _distance import DistanceUnit
from _fake_db import get_fake_db
from _garmin import GarminActivity
from _notion import NotionDatabase, NotionColumnType
from _time import TimeUnit


# region utilities

def check_is_valid_garmin_activity_field(field_name: str) -> None:
    garmin_activity_fields = GarminActivity.model_fields

    assert field_name in garmin_activity_fields, (
        f"Field '{field_name}' is not a valid Garmin activity field. "
        f"Available fields are: {', '.join(garmin_activity_fields.keys())}."
    )


def parse_compound_unit(raw_unit: str) -> tuple[str, str]:
    tokens = raw_unit.split('/')
    return tokens[0].strip(), tokens[1].strip()


# endregion utilities

class DataField(BaseModel):
    garmin_activity_field: Annotated[
        str,
        AfterValidator(check_is_valid_garmin_activity_field)
    ]
    notion_column_name: str


class DistanceField(DataField):
    unit: DistanceUnit


class DurationField(DataField):
    unit: TimeUnit


class SpeedField(DataField):
    distance_unit: Annotated[
        DistanceUnit,
        validate_as(str).transform(lambda raw_unit: DistanceUnit(parse_compound_unit(raw_unit)[0]))
    ] = Field(..., validation_alias='unit')
    time_unit: Annotated[
        TimeUnit,
        validate_as(str).transform(lambda raw_unit: TimeUnit(parse_compound_unit(raw_unit)[1]))
    ] = Field(..., validation_alias='unit')


class PaceField(DataField):
    time_unit: Annotated[
        TimeUnit,
        validate_as(str).transform(lambda raw_unit: TimeUnit(parse_compound_unit(raw_unit)[0]))
    ] = Field(..., validation_alias='unit')
    distance_unit: Annotated[
        DistanceUnit,
        validate_as(str).transform(lambda raw_unit: DistanceUnit(parse_compound_unit(raw_unit)[1]))
    ] = Field(..., validation_alias='unit')


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

    def __get_schema_for_data_field(self, data_field: DataField) -> NotionColumnSchema:
        raise NotImplementedError()
        return NotionColumnSchema(name=data_field.notion_column_name, valid_types=['TODO'])

    def __get_accepted_data_field_notion_types(self, data_field: DataField) -> list[NotionColumnType]:
        match data_field:
            case DistanceField():
                return [NotionColumnType.RICH_TEXT, ]
            case DurationField():
                return [NotionColumnType.NUMBER]
            case SpeedField():
                return [NotionColumnType.NUMBER]
            case PaceField():
                return [NotionColumnType.NUMBER]
            case _:
                return [NotionColumnType.RICH_TEXT]


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

        if validation_errors := self.__check_column_names_valid(database, database_schema):
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
    def __check_column_names_valid(
        database: NotionDatabase,
        database_schema: NotionDatabaseSchema,
    ) -> list[DatabaseValidationError] | None:
        """
        Checks if a column with the specified name exists in the database for every requested data field.
        Returns a validation error for every missing column.
        """
        validation_errors = []

        for expected_column_schema in database_schema.columns:
            if expected_column_schema.name not in (property.name for property in database.properties):
                validation_errors.append(
                    DatabaseValidationError(
                        message=f"Column '{expected_column_schema.name}' does not exist in the database."
                    )
                )

        return validation_errors


if __name__ == '__main__':
    try:
        fields = [
            # DataField.model_validate({
            #     'garmin_activity_field': 'id',
            #     'notion_column_name': 'ID',
            # }),
            DataField.model_validate({
                'garmin_activity_field': 'calories',
                'notion_column_name': 'Calories',
            }),
            DurationField.model_validate({
                'garmin_activity_field': 'duration',
                'notion_column_name': 'Duration (min)',
                'unit': 'm'
            }),
            DistanceField.model_validate({
                'garmin_activity_field': 'distance',
                'notion_column_name': 'Distance (km)',
                'unit': 'km'
            }),
            SpeedField.model_validate({
                'garmin_activity_field': 'average_speed',
                'notion_column_name': 'Speed',
                'unit': 'km/h'
            }),
            PaceField.model_validate({
                'garmin_activity_field': 'average_pace',
                'notion_column_name': 'Avg Pace',
                'unit': 's/km'
            }),
        ]
    except ValidationError as e:
        print(f"validation error: {e}")

    schema_factory = DatabaseSchemaFactory()
    database_schema = schema_factory.create('Activities', fields)

    database = NotionDatabase.model_validate(get_fake_db())

    validator = NotionDatabaseValidator()
    validation_errors = validator.validate_database(database, database_schema)

    if validation_errors:
        error_string = '\n'.join(error.message for error in validation_errors)
        print(f"Validation errors:\n{error_string}")

    assert 1
