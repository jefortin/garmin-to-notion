from __future__ import annotations

from src.core.garmin import GarminModel
from src.core.notion import NotionDatabase
from ._garmin_model_validator import IGarminModelValidator
from ._interface import ISynchronizationPlanValidator
from ._notion_database_validator import INotionDatabaseValidator
from .._synchronization_plan import SynchronizationPlan


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
