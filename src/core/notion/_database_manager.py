from typing import Generic, TypeVar, Callable

from notion_client import Client as NotionClient
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class NotionDatabaseManager(Generic[T]):
    """
    Provides the necessary operations to create, update and delete entries from a Notion database with the given
    specification.
    """

    def __init__(
        self,
        notion_client: NotionClient,
        database_id: str,
        id_column_name: str,
        garmin_to_notion_converter: Callable[[T], dict],
    ):
        self.__notion_client = notion_client
        self.__database_id = database_id
        self.__id_column_name = id_column_name
        self.__garmin_to_notion_converter = garmin_to_notion_converter

    def read(self, item_id: str) -> dict:
        """
        Retrieves the entry with the given row ID from the database.
        :raises ValueError: If the row with the given ID is not found.
        TODO: Convert the model back when reading.
        """
        query = self.__notion_client.databases.query(
            database_id=self.__database_id,
            filter={
                "and": [
                    {
                        "property": self.__id_column_name,
                        "unique_id": {
                            "equals": item_id,
                            "is_not_empty": True,
                        }
                    },
                ]
            }
        )

        results = query.get('results', [])

        if len(results) == 0:
            raise ValueError(f"Row with ID {item_id} not found in database {self.__database_id}")

        result, extra_results = results[0], results[1:]

        if extra_results:
            raise ValueError(f"Multiple rows with ID {item_id} found in database {self.__database_id}")

        return result

    def create(self, item: T, icon_url: str = None) -> None:
        """
        Creates a new entry in the database with the given data.
        TODO: Handle success / error
        """
        insert_model = self.__garmin_to_notion_converter(item)

        page = {
            "parent": {"database_id": self.__database_id},
            "properties": insert_model,
        }

        if icon_url:
            page["icon"] = {"type": "external", "external": {"url": icon_url}}

        self.__notion_client.pages.create(**page)

    def update(self, row_id: str, entry: T) -> None:
        """
        Updates the entry with the given row ID with the new data.
        """
        raise NotImplementedError
