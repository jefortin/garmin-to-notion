from __future__ import annotations

from datetime import timedelta
from functools import cached_property
from typing import Annotated, Optional

from pydantic import BaseModel, Field, NaiveDatetime, AliasPath, HttpUrl, computed_field, BeforeValidator
from pydantic.experimental.pipeline import validate_as

from _distance import DistanceUnit, Distance
from _pace import Pace
from _speed import Speed
from _time import TimeUnit

# region utilities

ACTIVITY_ICONS = {
    "Running": "https://img.icons8.com/?size=100&id=k1l1XFkME39t&format=png&color=000000",
    "Treadmill Running": "https://img.icons8.com/?size=100&id=9794&format=png&color=000000",
    "Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=000000",
    "Indoor Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=000000",
    "Swimming": "https://img.icons8.com/?size=100&id=9777&format=png&color=000000",
    "Indoor Cardio": "https://img.icons8.com/?size=100&id=62779&format=png&color=000000",
    "Walking": "https://img.icons8.com/?size=100&id=9807&format=png&color=000000",
    "Pilates": "https://img.icons8.com/?size=100&id=9774&format=png&color=000000",
    "Yoga": "https://img.icons8.com/?size=100&id=9783&format=png&color=000000",
    "Hiking": "https://img.icons8.com/?size=100&id=9844&format=png&color=000000",
    "Rowing": "https://img.icons8.com/?size=100&id=24889&format=png&color=000000",
    "Breathwork": "https://img.icons8.com/?size=100&id=9798&format=png&color=000000",
    "Strength Training": "https://img.icons8.com/?size=100&id=107640&format=png&color=000000",
    "Stretching": "https://img.icons8.com/?size=100&id=djfOcRn1m_kh&format=png&color=000000",
}

TRAINING_EFFECT_LABELS = {
    'NO': 'No Benefit',
    'MINOR': 'Some Benefit',
    'RECOVERY': 'Recovery',
    'MAINTAINING': 'Maintaining',
    'IMPROVING': 'Impacting',
    'IMPACTING': 'Impacting',
    'HIGHLY': 'Highly Impacting',
    'OVERREACHING': 'Overreaching',
}


def parse_icon_url(activity_type: str) -> HttpUrl | None:
    return ACTIVITY_ICONS.get(activity_type)


def parse_training_effect_label(training_effect_label: str) -> str:
    return training_effect_label.replace('_', ' ').title()


def parse_metabolism_effect(training_effect: str) -> str:
    """
    Parses the metabolism effect messages (aerobic and anaerobic) into a workable format.
    """
    message_token = next(iter(training_effect.split('_')), None)
    parsed_message = TRAINING_EFFECT_LABELS.get(message_token)

    if parsed_message is None:
        raise ValueError(f"Training effect '{training_effect}' is not a valid option")

    return parsed_message


def parse_distance_field(distance_meters: float) -> Distance:
    return Distance(distance_meters, DistanceUnit.METER)


def parse_duration_field(duration_seconds: float) -> timedelta:
    return timedelta(seconds=duration_seconds)


def parse_speed_field(speed_meter_per_second: float) -> Speed:
    return Speed(speed_meter_per_second, DistanceUnit.METER, TimeUnit.SECOND)


def parse_pace_from_speed(speed_meter_per_second: float) -> Pace:
    if speed_meter_per_second == 0:
        return Pace(0, TimeUnit.SECOND, DistanceUnit.METER)

    return Pace(1 / speed_meter_per_second, TimeUnit.SECOND, DistanceUnit.METER)


# endregion utilities

# region custom fields

TrainingEffectField = Annotated[Optional[str], BeforeValidator(parse_training_effect_label)]
MetabolismEffectField = Annotated[Optional[str], BeforeValidator(parse_metabolism_effect)]
DistanceField = Annotated[Distance, validate_as(float).transform(parse_distance_field)]
DurationField = Annotated[timedelta, validate_as(float).transform(parse_duration_field)]
SpeedField = Annotated[Speed, validate_as(float).transform(parse_speed_field)]
PaceField = Annotated[Pace, validate_as(float).transform(parse_pace_from_speed)]


# endregion custom fields

class GarminActivity(BaseModel):
    """
    Describes the data of a Garmin activity entry.
    TODO: This model is not complete, but only implements the currently used fields. Complete the model as needed.
    """

    start_time_utc: NaiveDatetime = Field(..., validation_alias='startTimeGMT')  # GMT and UTC are equivalent.
    id: int = Field(..., validation_alias='activityId')
    name: str = Field(..., validation_alias='activityName')
    type: str = Field(..., validation_alias=AliasPath('activityType', 'typeKey'))
    calories: float = Field(..., validation_alias='calories')
    is_personal_record: bool = Field(..., validation_alias='pr')
    training_effect: TrainingEffectField = Field(None, validation_alias='trainingEffectLabel')
    aerobic_effect: MetabolismEffectField = Field(None, validation_alias='aerobicTrainingEffectMessage')
    aerobic_score: Optional[float] = Field(None, validation_alias='aerobicTrainingEffect')
    anaerobic_effect: MetabolismEffectField = Field(None, validation_alias='anaerobicTrainingEffectMessage')
    anaerobic_score: Optional[float] = Field(None, validation_alias='anaerobicTrainingEffect')
    duration: DurationField = Field(..., validation_alias='duration')

    # TODO: Should we set the following fields to None if their value is 0?
    distance: DistanceField = Field(..., validation_alias='distance')
    average_speed: SpeedField = Field(..., validation_alias='averageSpeed')
    average_pace: PaceField = Field(..., validation_alias='averageSpeed')

    @computed_field
    @cached_property
    def icon_url(self) -> HttpUrl | None:
        return ACTIVITY_ICONS.get(self.activity_type)
