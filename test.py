from typing import Literal, Annotated, Union

from pydantic import BaseModel, Field, UUID4


# region database

class DatabaseColumn(BaseModel):
    id: str
    name: str
    type: str


class TestDatabase(BaseModel):
    id: UUID4
    properties: dict[str, DatabaseColumn]


# endregion database

# region columns



# endregion columns


if __name__ == '__main__':
    import os
    from garminconnect import Garmin
    from notion_client import Client

    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DB_ID")

    # Initialize Garmin client and login
    # garmin = Garmin(garmin_email, garmin_password)
    # garmin.login()
    notion_client = Client(auth=notion_token)

    # Get all activities
    notion_database = notion_client.databases.retrieve(database_id)
    parsed_database = TestDatabase.model_validate(notion_database)

    assert 1
