from src.core.notion import NotionColumnType
from ._models import BridgeModel
from ._synchronization_plan import SynchronizedField


class NotionColumnSchema(BridgeModel):
    """
    Describes the expected schema of a Notion column.
    """
    name: str
    valid_types: list[NotionColumnType]


class NotionDatabaseSchema(BridgeModel):
    """
    Describes the expected schema of a Notion database.
    """
    name: str
    columns: list[NotionColumnSchema]


class DatabaseSchemaFactory:
    def create(self, database_title: str, synchronized_fields: list[SynchronizedField]) -> NotionDatabaseSchema:
        return NotionDatabaseSchema(
            name=database_title,
            columns=[
                self.__get_schema_for_data_field(data_field)
                for data_field in synchronized_fields
            ]
        )

    @staticmethod
    def __get_schema_for_data_field(synchronized_field: SynchronizedField) -> NotionColumnSchema:
        return NotionColumnSchema(
            name=synchronized_field.notion_column_name,
            valid_types=list(synchronized_field.field_type.get_column_type_adapters().keys())
        )
