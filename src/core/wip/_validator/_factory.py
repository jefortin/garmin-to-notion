from ._garmin_model_validator import GarminModelValidatorFactory
from ._interface import ISynchronizationPlanValidator
from ._notion_database_validator import NotionDatabaseValidatorFactory
from ._v1 import SynchronizationPlanValidatorV1


class SynchronizationPlanValidatorFactory:
    """
    Factory for creating the ISynchronizationPlanValidator instance to use for validating synchronization plans.
    """

    def create(self) -> ISynchronizationPlanValidator:
        return SynchronizationPlanValidatorV1(
            notion_database_validator=NotionDatabaseValidatorFactory().create(),
            garmin_model_validator=GarminModelValidatorFactory().create(),
        )
