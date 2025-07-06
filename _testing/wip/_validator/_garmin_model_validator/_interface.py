from abc import ABC, abstractmethod

from src.core.garmin import GarminModel
from .._synchronization_plan_validator import SynchronizationPlanValidationError
from ..._synchronization_plan import SynchronizationPlan


class GarminModelValidationError(SynchronizationPlanValidationError):
    """
    Validation error specific to the IGarminModelValidator logic.
    """
    ...


class IGarminModelValidator(ABC):
    """
    Allows validating a Garmin model against a synchronization plan.
    """

    @abstractmethod
    def validate_model(
        self,
        garmin_model: type[GarminModel],
        synchronization_plan: SynchronizationPlan,
    ) -> list[GarminModelValidationError]:
        """
        Validates that a Notion database matches the expected schema.
        Returns a list of validation errors if the database does not match the schema.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """
        ...


class GarminModelValidatorFactory:
    """
    Factory for creating the IGarminModelValidator instance to use for validating Garmin models.
    """

    @staticmethod
    def create() -> IGarminModelValidator:
        from ._v1 import GarminModelValidatorV1
        return GarminModelValidatorV1()
