from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar, Any

from src.core.garmin import GarminModel
from src.core.notion import NotionDatabase, NotionColumnType
from ._models import BridgeModel
from ._synchronization_plan import SynchronizedField

TGarmin = TypeVar('TGarmin', bound=GarminModel)


class GarminToNotionColumnConverter(BridgeModel):
    garmin_field_name: str
    notion_column_name: str
    column_type: NotionColumnType
    column_type_adapter: Callable[[Any], Any]


class GarminToNotionConverter(BridgeModel, Generic[TGarmin]):
    """
    Converts a Garmin model to a Notion database row insert block.
    Fields are assumed to have been validated when using this class.
    """
    column_converters: list[GarminToNotionColumnConverter]

    def get_insert_payload(self, garmin_model_instance: TGarmin) -> dict:
        """
        Converts the provided Garmin model instance into a dictionary representation that can be used to create or
        update a Notion database entry.
        """
        insert_template = {}

        for column_converter in self.column_converters:
            garmin_field_name = column_converter.garmin_field_name
            notion_column_name = column_converter.notion_column_name

            try:
                garmin_field_value = getattr(garmin_model_instance, garmin_field_name)
            except AttributeError:
                raise ValueError(
                    f"Garmin model '{self.__garmin_model.__name__}' does not have field '{garmin_field_name}'."
                )

            # TODO: Properly handle None values.
            notion_column_value = column_converter.column_type_adapter(garmin_field_value)
            notion_column_insert_payload = column_converter.column_type.get_insert_payload(notion_column_value)
            insert_template[notion_column_name] = notion_column_insert_payload

        return insert_template


class GarminToNotionConverterFactory(Generic[TGarmin]):
    """
    Converts a Garmin model to a Notion database row.
    Fields are assumed to have been validated when using this class.
    """

    def create(
        self,
        database: NotionDatabase,
        data_fields: list[SynchronizedField],
    ) -> GarminToNotionConverter[TGarmin]:
        notion_column_types = {
            column.name: column.type
            for column in database.properties
        }

        column_converters = []

        for data_field in data_fields:
            data_field_column_type = notion_column_types[data_field.notion_column_name]
            column_type_adapter = data_field.get_column_type_adapters()[data_field_column_type]
            column_converters.append(
                GarminToNotionColumnConverter(
                    garmin_field_name=data_field.garmin_field_name,
                    notion_column_name=data_field.notion_column_name,
                    column_type=data_field_column_type,
                    column_type_adapter=column_type_adapter,
                )
            )

        return GarminToNotionConverter(
            column_converters=column_converters,
        )
