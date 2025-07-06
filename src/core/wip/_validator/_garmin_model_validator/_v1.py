from src.core.garmin import GarminModel
from ._interface import GarminModelValidationError, IGarminModelValidator
from ..._synchronization_plan import SynchronizationPlan, SynchronizedField


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
        field_errors = []

        for field in synchronization_plan.synchronized_fields:
            field_error = self.__check_garmin_field_is_valid(field, garmin_model)

            if field_error is not None:
                field_errors.append(field_error)

        return field_errors

    @staticmethod
    def __check_garmin_field_is_valid(
        synchronized_field: SynchronizedField,
        garmin_model: type[GarminModel]
    ) -> GarminModelValidationError | None:
        garmin_model_fields = garmin_model.model_fields

        if not synchronized_field.garmin_field_name in garmin_model_fields:
            return GarminModelValidationError(
                message=(
                    f"Field '{synchronized_field.garmin_field_name}' is not a valid Garmin activity field. "
                    f"Available fields are: {', '.join(garmin_model_fields.keys())}."
                )
            )

        return None
