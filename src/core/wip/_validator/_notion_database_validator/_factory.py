from ._database_schema import DatabaseSchemaFactory
from ._interface import INotionDatabaseValidator
from ._v1 import NotionDatabaseValidatorV1


class NotionDatabaseValidatorFactory:
    """
    Factory for creating the INotionDatabaseValidator instance to use for validating Notion databases.
    """

    def create(self) -> INotionDatabaseValidator:
        return NotionDatabaseValidatorV1(DatabaseSchemaFactory())
