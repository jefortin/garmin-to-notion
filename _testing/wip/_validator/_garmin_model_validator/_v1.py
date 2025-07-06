from _testing.wip._synchronization_plan import SynchronizationPlan
from _testing.wip._validator._garmin_model_validator._interface import IGarminModelValidator, GarminModelValidationError
from src.core.garmin import GarminModel


class GarminModelValidatorV1(IGarminModelValidator):
    """
    Garmin Model Validator for version 1.
    This class implements the validation logic for Garmin models.
    """

    def validate_model(
        self,
        garmin_model: type[GarminModel],
        synchronization_plan: SynchronizationPlan,
    ) -> list[GarminModelValidationError]:
        raise NotImplementedError("GarminModelValidatorV1 is not yet implemented.")
