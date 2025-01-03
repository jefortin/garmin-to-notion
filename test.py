from typing import Literal, Annotated, Union

from pydantic import BaseModel, Field, UUID4


class DatabaseColumnText(BaseModel):
    """
    See: https://developers.notion.com/reference/property-object#rich-text
    """

    id: str
    name: str
    type: Literal["rich_text"]
    # The `rich_text` property is always empty.


class DatabaseColumnTitle(BaseModel):
    """
    See: https://developers.notion.com/reference/property-object#title
    """

    id: str
    type: Literal["title"]
    # The `title` property is always empty.


class DatabaseColumnNumber(BaseModel):
    """
    See: https://developers.notion.com/reference/property-object#number
    """

    class NumberFormat(BaseModel):
        format: Literal['number', 'number_with_commas', 'percent', 'dollar']  # See link for full list

    id: str
    type: Literal["number"]
    format: NumberFormat


class DatabaseColumnDate(BaseModel):
    """
    See: https://developers.notion.com/reference/property-object#date
    """

    id: str
    type: Literal["date"]
    # The `date` property is always empty.


class DatabaseColumn(BaseModel):
    id: str
    name: str


# # Field type representing a Notion database column.
# # See: https://developers.notion.com/docs/working-with-databases#database-properties
# DatabaseColumn = Annotated[
#     Union[
#         DatabaseColumnText,
#         DatabaseColumnTitle,
#         DatabaseColumnNumber,
#         DatabaseColumnDate,
#     ],
#     Field(discriminator='type'),
# ]


class TestDatabase(BaseModel):
    id: UUID4
    properties: dict[str, DatabaseColumn]


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
