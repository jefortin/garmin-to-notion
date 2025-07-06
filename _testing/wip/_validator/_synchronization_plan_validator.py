from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import Field

from src.core.garmin import GarminModel
from src.core.notion import NotionDatabase
from ._garmin_model_validator import IGarminModelValidator, GarminModelValidatorFactory
from ._notion_database_validator import INotionDatabaseValidator, NotionDatabaseValidatorFactory
from .._models import BridgeModel
from .._synchronization_plan import SynchronizationPlan


class SynchronizationPlanValidationError(BridgeModel):
    message: str = Field(..., description="Human-readable error message describing why the validation failed.")


class ISynchronizationPlanValidator(ABC):
    """
    Interface for validating synchronization plans.
    """

    @abstractmethod
    def validate_synchronization_plan(
        self,
        synchronization_plan: SynchronizationPlan,
        notion_database: NotionDatabase,
        garmin_model: type[GarminModel],
    ) -> list[SynchronizationPlanValidationError]:
        """
        Validates that a synchronization plan matches the expected schema.
        Returns a list of validation errors if the plan does not match the schema.
        If no errors are returned, the synchronization plan can be considered compatible with the specification.
        """
        ...


class SynchronizationPlanValidatorFactory:
    """
    Factory for creating the ISynchronizationPlanValidator instance to use for validating synchronization plans.
    """

    @staticmethod
    def create() -> ISynchronizationPlanValidator:
        return SynchronizationPlanValidatorV1(
            notion_database_validator=NotionDatabaseValidatorFactory.create(),
            garmin_model_validator=GarminModelValidatorFactory.create(),
        )


class SynchronizationPlanValidatorV1(ISynchronizationPlanValidator):
    """
    First iteration of an ISynchronizationPlanValidator implementation.
    """

    def __init__(
        self,
        notion_database_validator: INotionDatabaseValidator,
        garmin_model_validator: IGarminModelValidator,
    ):
        self.__notion_database_validator = notion_database_validator
        self.__garmin_model_validator = garmin_model_validator

    def validate_synchronization_plan(
        self,
        synchronization_plan: SynchronizationPlan,
        notion_database: NotionDatabase,
        garmin_model: type[GarminModel],
    ) -> list[SynchronizationPlanValidationError]:
        notion_database_validation_errors = self.__notion_database_validator.validate_database(
            database=notion_database,
            synchronization_plan=synchronization_plan,
        )

        if notion_database_validation_errors:
            # Stop validation if the Notion DB is invalid, because the Garmin model validation errors only make sense
            # if the synchronization plan matches the Notion database.
            return notion_database_validation_errors

        garmin_model_validation_errors = self.__garmin_model_validator.validate_model(
            garmin_model=garmin_model,
            synchronization_plan=synchronization_plan,
        )

        return garmin_model_validation_errors
