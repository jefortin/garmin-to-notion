from __future__ import annotations

import uuid
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, UUID4, Field, AfterValidator
from pydantic.experimental.pipeline import validate_as


# region utilities

def parse_database_titles(database_title_data: list[dict]) -> list[str]:
    """
    Extracts the plain text title from the database title data.
    A database can have multiple titles, so every title should be included as any can properly reference the database.
    See: https://developers.notion.com/reference/database
    """
    return [
        title_object['plain_text']
        for title_object in database_title_data
    ]


def parse_database_properties(database_properties: dict[str, 'NotionDatabaseColumn']) -> list['NotionDatabaseColumn']:
    """
    Extracts the database properties from the database properties data.
    """
    return list(database_properties.values())


# endregion utilities

# region custom types

DatabaseTitleField = Annotated[list[str], validate_as(list).transform(parse_database_titles)]
DatabaseColumnsField = Annotated[
    list['NotionDatabaseColumn'],
    validate_as(dict[str, 'NotionDatabaseColumn']).transform(parse_database_properties),
]
UuidString = Annotated[str, AfterValidator(lambda uuid_string: uuid.UUID(uuid_string, version=4))]


# endregion custom types


class NotionColumnType(Enum):
    """
    Represents the different types of columns that can be in a Notion database
    See: https://developers.notion.com/reference/property-object
    """
    UNIQUE_ID = 'unique_id'
    CHECKBOX = 'checkbox'
    CREATED_BY = 'created_by'
    CREATED_TIME = 'created_time'
    DATE = 'date'
    EMAIL = 'email'
    FILES = 'files'
    FORMULA = 'formula'
    LAST_EDITED_BY = 'last_edited_by'
    LAST_EDITED_TIME = 'last_edited_time'
    MULTI_SELECT = 'multi_select'
    NUMBER = 'number'
    PEOPLE = 'people'
    PHONE_NUMBER = 'phone_number'
    RELATION = 'relation'
    RICH_TEXT = 'rich_text'
    ROLLUP = 'rollup'
    SELECT = 'select'
    STATUS = 'status'
    TITLE = 'title'
    URL = 'url'


class NotionDatabaseColumn(BaseModel):
    id: str
    name: str
    type: NotionColumnType


class NotionDatabase(BaseModel):
    id: UUID4 | UuidString = Field(..., validation_alias='id')
    names: DatabaseTitleField = Field(..., validation_alias='title')
    properties: Annotated[
        list[NotionDatabaseColumn],
        validate_as(dict[str, NotionDatabaseColumn]).transform(lambda properties: properties.values()),
    ] = Field(..., validation_alias='properties')
