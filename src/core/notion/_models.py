from __future__ import annotations

import uuid
from enum import Enum
from typing import Annotated, Callable, Any

from pydantic import BaseModel, UUID4, Field, AfterValidator
from pydantic.experimental.pipeline import validate_as


class NotionModel(BaseModel):
    """
    Base class for all pydantic models representing Notion entities.
    """
    ...


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

    __data_templates: dict[NotionColumnType, Callable[[Any], dict]] = {
        # Mapping of the expected data format for each column type.
        # See: https://developers.notion.com/reference/page-property-values#type-objects
        # TODO: Not all types are supported yet to simplify the logic.
        UNIQUE_ID: lambda value: {'unique_id': value},
        CHECKBOX: lambda value: {'checkbox': value},
        # CREATED_BY: lambda value: {'created_by': value}, # Not supported for inserts.
        # CREATED_TIME: lambda value: {'created_time': value}, # Not supported for inserts.
        DATE: lambda value: {'date': {'start': value}},
        EMAIL: lambda value: {'email': value},
        # FILES: {}  # TODO
        # FORMULA: {},  # TODO
        # LAST_EDITED_BY: {}, # Not supported for inserts.
        # LAST_EDITED_TIME: {}, # Not supported for inserts.
        # MULTI_SELECT: {} # TODO
        NUMBER: lambda value: {'number': value},
        # PEOPLE: {}, # TODO
        PHONE_NUMBER: lambda value: {'phone_number': value},
        RELATION: {},  # TODO
        RICH_TEXT: lambda value: {'rich_text': [{'text': {'content': value}}]},
        ROLLUP: {},  # Not supported for inserts.
        SELECT: lambda value: {'select': {'name': value}},
        STATUS: lambda value: {'status': {'name': value}},
        TITLE: lambda value: {'title': [{'text': {'content': value}}]},
        URL: lambda value: {'url': value},
    }

    def get_insert_payload(self, data: Any):
        """
        Formats the provided data into a dictionary representation based on the column type that can be used to
        create or update a database entry.
        The data is expected to be in the format that the Notion API accepts for this column type.
        """
        self.__data_templates: dict[NotionColumnType, Callable[[Any], dict]]

        if self.value not in self.__data_templates:
            raise ValueError(f"Unsupported column type: {self}")

        return self.__data_templates[self.value](data)


class NotionDatabaseColumn(NotionModel):
    id: str
    name: str
    type: NotionColumnType


class NotionDatabase(NotionModel):
    id: UUID4 | UuidString = Field(..., validation_alias='id')
    names: DatabaseTitleField = Field(..., validation_alias='title')
    properties: Annotated[
        list[NotionDatabaseColumn],
        validate_as(dict[str, NotionDatabaseColumn]).transform(lambda properties: properties.values()),
    ] = Field(..., validation_alias='properties')
