from __future__ import annotations

from _fake_activities import get_fake_activities
from _garmin import GarminActivity

# region bridge

# class GarminActivityFieldSpecification(BaseModel):
#     ...
#
#
# class GarminActivityField(Enum):
#     """
#     Describes a Garmin activity data field to sync to the Notion database.
#     """
#
#     @abstractmethod
#     def _get_field_specification(self) -> GarminActivityFieldSpecification:
#         """
#         Retrieve the specification of the field.
#         Used for validating that the database format is valid.
#         """
#         ...


# class DataField(BaseModel):
#     garmin_activity_field: GarminActivityField
#     notion_column_name: str


# class GarminDistanceField(BaseModel):
#     garmin_activity_field: str
#     notion_column_name: str
#     unit: DistanceUnit


# endregion bridge


if __name__ == '__main__':
    import os

    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DB_ID")

    # Initialize API clients
    # notion_client = Client(auth=notion_token)
    # garmin_client = Garmin(garmin_email, garmin_password)
    # garmin_client.login()

    # Validate Notion database
    # notion_database = notion_client.databases.retrieve(database_id)
    # parsed_database = NotionDatabase.model_validate(notion_database)
    # TODO:
    #  id_fields = []
    #  data_fields = []

    # get Garmin activities
    # raw_garmin_activities = garmin_client.get_activities(0, 100)
    raw_garmin_activities = get_fake_activities()
    garmin_activities = (
        GarminActivity.model_validate(activity)
        for activity in raw_garmin_activities
    )
c
    assert 1
