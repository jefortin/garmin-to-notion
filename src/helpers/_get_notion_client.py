import os
from dataclasses import dataclass

from notion_client import Client

@dataclass(frozen=True)
class NotionConfiguration:
    activities_database_id: str
    personal_records_database_id: str
    sleep_database_id: str
    daily_steps_database_id: str


def get_notion_client() -> tuple[Client, NotionConfiguration]:
    print("Initializing Notion client...")

    notion_databases = NotionConfiguration(
        activities_database_id=os.getenv("NOTION_DB_ID"),
        personal_records_database_id=os.getenv("NOTION_PR_DB_ID"),
        sleep_database_id=os.getenv("NOTION_SLEEP_DB_ID"),
        daily_steps_database_id=os.getenv("NOTION_STEPS_DB_ID"),
    )

    notion_token = os.getenv("NOTION_TOKEN")
    notion_client = Client(auth=notion_token)

    print("Notion client initialized.")

    return notion_client, notion_databases