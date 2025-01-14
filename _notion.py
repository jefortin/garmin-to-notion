from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, UUID4


class NotionColumnSchema(BaseModel):
    """
    Describes the expected schema of a Notion column.
    """
    name: str
    type: Literal[
        'checkbox',
        'created_by',
        'created_time',
        'date',
        'email',
        'files',
        'formula',
        'last_edited_by',
        'last_edited_time',
        'multi_select',
        'number',
        'people',
        'phone_number',
        'relation',
        'rich_text',
        'rollup',
        'select',
        'status',
        'title',
        'url',
    ]  # See: https://developers.notion.com/reference/property-object


class ValidationError(BaseModel):
    message: str


class NotionDatabaseSchema(BaseModel):
    """
    Describes the expected schema of a Notion database.
    """
    name: str
    columns: list[NotionColumnSchema]


class NotionDatabaseColumn(BaseModel):
    id: str
    name: str
    type: str


class NotionDatabase(BaseModel):
    id: UUID4
    properties: dict[str, NotionDatabaseColumn]


class NotionDatabaseValidator:
    def validate_database(
        self,
        database: NotionDatabase,
        database_schema: NotionDatabaseSchema,
    ) -> list[ValidationError]:
        """
        Validates that a Notion database matches the expected schema.
        Returns a list of validation errors if the database does not match the schema.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """
        raise NotImplementedError("Database validation not implemented.")
