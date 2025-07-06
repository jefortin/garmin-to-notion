from abc import ABC, abstractmethod

from src.core.notion import NotionDatabase
from ._v1 import NotionDatabaseValidatorV1
from .._synchronization_plan_validator import SynchronizationPlanValidationError
from ..._synchronization_plan import SynchronizationPlan


class DatabaseValidationError(SynchronizationPlanValidationError):
    """
    Validation error specific to the INotionDatabaseValidator logic.
    """
    ...


class INotionDatabaseValidator(ABC):
    """
    Allows validating a Notion database against a schema.
    """

    @abstractmethod
    def validate_database(
        self,
        database: NotionDatabase,
        synchronization_plan: SynchronizationPlan,
    ) -> list[DatabaseValidationError]:
        """
        Validates that a Notion database matches the expected schema.
        Returns a list of validation errors if the database does not match the schema.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """
        ...


class NotionDatabaseValidatorFactory:
    """
    Factory for creating the INotionDatabaseValidator instance to use for validating Notion databases.
    """

    @staticmethod
    def create() -> INotionDatabaseValidator:
        return NotionDatabaseValidatorV1()
