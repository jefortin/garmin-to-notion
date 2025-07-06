from __future__ import annotations

from src.core.garmin import GarminModel
from src.core.notion import NotionDatabase
from src.core.synchronizer._activities._models import GarminActivity
from src.core.types import DistanceUnit, TimeUnit
from ._database_schema import DatabaseSchemaFactory
from ._garmin_to_notion_converter import GarminToNotionConverterFactory
from ._synchronization_plan import (
    NumberField,
    TextField,
    DateField,
    DistanceField,
    PaceField,
    TrueFalseField,
    SpeedField,
    DurationField,
    SynchronizationPlan, SynchronizedField,
)
from ._validator import (
    SynchronizationPlanValidatorFactory,
)

# region data fields
activity_data_fields: list[SynchronizedField] = [
    SynchronizedField(
        garmin_field_name='id',
        notion_column_name='Activity ID',
        field_type=NumberField(
            precision=0,
        )
    ),
    SynchronizedField(
        garmin_field_name='name',
        notion_column_name='Activity Name',
        field_type=TextField(
            default='Unknown',
        )
    ),
    SynchronizedField(
        garmin_field_name='start_time',
        notion_column_name='Date',
        field_type=DateField(
            timezone='UTC',
        )
    ),
    SynchronizedField(
        garmin_field_name='distance',
        notion_column_name='Distance (km)',
        field_type=DistanceField(
            unit=DistanceUnit.KILOMETER,
        )
    ),
    SynchronizedField(
        garmin_field_name='duration',
        notion_column_name='Duration (min)',
        field_type=DurationField(
            unit=TimeUnit.MINUTE,
        )
    ),
    SynchronizedField(
        garmin_field_name='calories',
        notion_column_name='Calories',
        field_type=NumberField(
            precision=0,
        )
    ),
    SynchronizedField(
        garmin_field_name='average_pace',
        notion_column_name='Avg Pace',
        field_type=PaceField(
            time_unit=TimeUnit.SECOND,
            distance_unit=DistanceUnit.KILOMETER,
        )
    ),
    SynchronizedField(
        garmin_field_name='training_effect',
        notion_column_name='Training Effect',
        field_type=TextField(
            default='Unknown',
        )
    ),
    SynchronizedField(
        garmin_field_name='aerobic_score',
        notion_column_name='Aerobic',
        field_type=NumberField(
            precision=2,
        )
    ),
    SynchronizedField(
        garmin_field_name='aerobic_effect',
        notion_column_name='Aerobic Effect',
        field_type=TextField(
            default='Unknown',
        )
    ),
    SynchronizedField(
        garmin_field_name='anaerobic_score',
        notion_column_name='Anaerobic',
        field_type=NumberField(
            precision=2,
        )
    ),
    SynchronizedField(
        garmin_field_name='anaerobic_effect',
        notion_column_name='Anaerobic Effect',
        field_type=TextField(
            default='Unknown',
        )
    ),
    SynchronizedField(
        garmin_field_name='is_personal_record',
        notion_column_name='PR',
        field_type=TrueFalseField(
        )
    ),
    SynchronizedField(
        garmin_field_name='type',
        notion_column_name='Activity Type',
        field_type=TextField(
            default='Unknown',
        )
    ),
    SynchronizedField(
        garmin_field_name='average_speed',
        notion_column_name='Speed',
        field_type=SpeedField(
            distance_unit=DistanceUnit.KILOMETER,
            time_unit=TimeUnit.HOUR,
        )
    ),
    SynchronizedField(
        garmin_field_name='bad field',
        notion_column_name='Activity Type',
        field_type=TextField(
            default='Unknown',
        )
    ),
]


# endregion data fields

def get_notion_database(notion_token: str, database_id: str, *, use_fake_database: bool) -> NotionDatabase:
    if use_fake_database:
        from .._fakes._fake_db import get_fake_db
        raw_notion_database = NotionDatabase.model_validate(get_fake_db())
    else:
        from notion_client import Client as NotionClient

        notion_client = NotionClient(auth=notion_token)

        raw_notion_database = notion_client.databases.retrieve(database_id)

    return NotionDatabase.model_validate(raw_notion_database)


def get_garmin_activities(garmin_username: str, garmin_password: str, *, use_fake_activities: bool) -> list[
    GarminActivity]:
    if use_fake_activities:
        from .._fakes._fake_activities import get_fake_activities
        raw_activities = get_fake_activities()
    else:
        from garminconnect import Garmin as GarminClient

        garmin_client = GarminClient(garmin_username, garmin_password)
        garmin_client.login()

        raw_activities = garmin_client.get_activities(0, 10)

    return [GarminActivity.model_validate(activity) for activity in raw_activities]


if __name__ == '__main__':
    import os

    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DB_ID")

    database_schema = DatabaseSchemaFactory().create('Activity Database', activity_data_fields)

    synchronization_plan = SynchronizationPlan(
        notion_database_schema=database_schema,
        synchronized_fields=activity_data_fields,
    )

    garmin_model: type[GarminModel] = GarminActivity
    notion_database: NotionDatabase = get_notion_database(notion_token, database_id, use_fake_database=False)

    validator = SynchronizationPlanValidatorFactory().create()
    validation_errors = validator.validate_synchronization_plan(
        synchronization_plan,
        notion_database,
        garmin_model,
    )

    if validation_errors:
        error_string = '\n'.join(error.message for error in validation_errors)
        print(f"Validation errors:\n{error_string}")
        exit()

    garmin_activities = get_garmin_activities(garmin_email, garmin_password, use_fake_activities=True)
    garmin_activity = garmin_activities[0]

    converter_factory = GarminToNotionConverterFactory[GarminActivity]()
    converter = converter_factory.create(notion_database, activity_data_fields)

    # insert_block = converter.get_insert_payload(garmin_activity)

    raise NotImplementedError('Subclass NotionDatabaseManager')
    notion_database = NotionDatabaseManager(notion_client, database_id, "ID", converter.get_insert_payload)

    if not notion_database.read(garmin_activity.id):
        notion_database.create(garmin_activity, garmin_activity.icon_url)
    assert 1
