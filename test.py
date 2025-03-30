from __future__ import annotations

from notion_client import Client as NotionClient

from _fake_activities import get_fake_activities
from _fake_db import get_fake_db
from _garmin import GarminActivity
from _notion import NotionDatabase



if __name__ == '__main__':
    import os

    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DB_ID")

    # Initialize API clients
    notion_client = NotionClient(auth=notion_token)
    # garmin_client = Garmin(garmin_email, garmin_password)
    # garmin_client.login()

    # Validate Notion database
    # notion_database = get_fake_db()
    notion_database = notion_client.databases.retrieve(database_id)
    parsed_database = NotionDatabase.model_validate(notion_database)
    # TODO:
    #  id_fields = []
    #  data_fields = []

    # get Garmin activities
    # raw_garmin_activities = garmin_client.get_activities(0, 100)
    # raw_garmin_activities = get_fake_activities()
    # garmin_activities = (
    #     GarminActivity.model_validate(activity)
    #     for activity in raw_garmin_activities
    # )

    assert 1
