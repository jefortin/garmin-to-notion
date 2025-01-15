from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, UUID4, Field
from pydantic.experimental.pipeline import validate_as


class NotionDatabaseColumn(BaseModel):
    id: str
    name: str
    type: str


class NotionDatabase(BaseModel):
    id: UUID4 = Field(..., validation_alias='id')
    name: Annotated[
        str,
        validate_as(list).transform(lambda title_list: title_list[0]['plain_text'])
    ] = Field(..., validation_alias='title')
    properties: Annotated[
        list[NotionDatabaseColumn],
        validate_as(dict[str, NotionDatabaseColumn]).transform(lambda properties: properties.values()),
    ] = Field(..., validation_alias='properties')
