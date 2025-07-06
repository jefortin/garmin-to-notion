from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import Field

from src.core.garmin import GarminModel
from src.core.notion import NotionDatabase
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
