from __future__ import annotations

from abc import abstractmethod
from datetime import timedelta
from enum import Enum
from functools import cached_property
from typing import Literal, Annotated

from pydantic import BaseModel, Field, UUID4, NaiveDatetime, AliasPath, HttpUrl, computed_field, BeforeValidator

from _distance import DistanceUnit, Distance
from _pace import Pace
from _speed import Speed
from _time import TimeUnit


# region database

class DatabaseColumn(BaseModel):
    id: str
    name: str
    type: str


class NotionDatabase(BaseModel):
    id: UUID4
    properties: dict[str, DatabaseColumn]


# endregion database

# region columns

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


class GarminActivity(BaseModel):
    """
    Describes the data of a Garmin activity entry.
    TODO: This model is not complete, but only implements the currently used fields. Complete the model as needed.
    """

    @staticmethod
    def __parse_training_effect_label(training_effect_label: str) -> str:
        return training_effect_label.replace('_', ' ').title()

    @staticmethod
    def __parse_training_effect(training_effect: str) -> str:
        message_token = next(iter(training_effect.split('_')), None)

        match message_token:
            case 'NO':
                return 'No Benefit'
            case 'MINOR':
                return 'Some Benefit'
            case 'RECOVERY':
                return 'Recovery'
            case 'MAINTAINING':
                return 'Maintaining'
            case 'IMPROVING':
                return 'Impacting'
            case 'IMPACTING':
                return 'Impacting'
            case 'HIGHLY':
                return 'Highly Impacting'
            case 'OVERREACHING':
                return 'Overreaching'
            case _:
                raise ValueError(f"Training effect '{training_effect}' is not a valid option")

    start_time_utc: NaiveDatetime = Field(
        ...,
        validation_alias='startTimeGMT',  # GMT and UTC are considered equivalent.
    )
    id: int = Field(..., validation_alias='activityId')
    name: str = Field(..., validation_alias='activityName')
    type: str = Field(..., validation_alias=AliasPath('activityType', 'typeKey'))
    calories: float = Field(..., validation_alias='calories')
    is_personal_record: bool = Field(..., validation_alias='pr')
    training_effect: Annotated[
        str,
        Field(..., validation_alias='trainingEffectLabel'),
        BeforeValidator(__parse_training_effect_label),
    ]
    aerobic_effect: Annotated[
        str,
        Field(..., validation_alias='aerobicTrainingEffectMessage'),
        BeforeValidator(__parse_training_effect),
    ]
    aerobic_score: float = Field(..., validation_alias='aerobicTrainingEffect')
    anaerobic_effect: Annotated[
        str,
        Field(..., validation_alias='anaerobicTrainingEffectMessage'),
        BeforeValidator(__parse_training_effect),
    ]
    anaerobic_score: float = Field(..., validation_alias='anaerobicTrainingEffect')

    # __distance_meters: float = Field(..., alias='distance')  # Private to prefer using the `distance` field instead.
    # __duration_seconds: float = Field(..., alias='duration')  # Private to prefer using the `duration` instead.
    # __average_speed_meter_per_second: float = Field(..., alias='averageSpeed')

    @computed_field
    @cached_property
    def icon_url(self) -> HttpUrl | None:
        return ACTIVITY_ICONS.get(self.activity_type)

    @computed_field()
    @cached_property
    def distance(self) -> Distance:
        return Distance(self.__distance_meters, DistanceUnit.METER)

    @computed_field()
    @cached_property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.__duration_seconds)

    @computed_field()
    @cached_property
    def average_speed(self) -> Speed:
        return Speed(self.__average_speed_meter_per_second, DistanceUnit.METER, TimeUnit.SECOND)

    @computed_field()
    @cached_property
    def average_pace(self) -> Pace:
        return Pace(1 / self.__average_speed_meter_per_second, TimeUnit.SECOND, DistanceUnit.METER)


class GarminActivityFieldSpecification(BaseModel):
    ...


class GarminActivityField(Enum):
    """
    Describes a Garmin activity data field to sync to the Notion database.
    """

    @abstractmethod
    def _get_field_specification(self) -> GarminActivityFieldSpecification:
        """
        Retrieve the specification of the field.
        Used for validating that the database format is valid.
        """
        ...


class DataField(BaseModel):
    garmin_activity_field: GarminActivityField
    notion_column_name: str


class GarminDistanceField(BaseModel):
    garmin_activity_field: str
    notion_column_name: str
    unit: DistanceUnit


class NotionColumnSpecification(BaseModel):
    """
    Describes the requirements for a Notion column.
    """
    name: str
    type: Literal[
        'checkbox',
        'created_by',
        'created_time',
        'date',
        'email',
        'files',
        'formula',
        'last_edited_by',
        'last_edited_time',
        'multi_select',
        'number',
        'people',
        'phone_number',
        'relation',
        'rich_text',
        'rollup',
        'select',
        'status',
        'title',
        'url',
    ]  # See: https://developers.notion.com/reference/property-object


class ValidationError(BaseModel):
    message: str


class NotionDatabaseSpecification(BaseModel):
    """
    Describes the requirements for a Notion database.
    """
    name: str
    columns: list[NotionColumnSpecification]

    def get_validation_errors(self, notion_database: NotionDatabase) -> list[ValidationError]:
        """
        Validates a Notion database against the specification and returns a list of validation errors.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """
        raise NotImplementedError("Specification validation not implemented.")


# endregion columns

# region temp

def get_fake_activities() -> list[dict]:
    return [
        {
            'activityId': 17983525606,
            'activityName': '60 min Two for One: Power Zone Ride with Denis & Matt',
            'activityTrainingLoad': 135.3037872314453,
            'activityType': {
                'isHidden': False,
                'parentTypeId': 2,
                'restricted': False,
                'trimmable': True,
                'typeId': 25,
                'typeKey': 'indoor_cycling'
            },
            'aerobicTrainingEffect': 3.700000047683716,
            'aerobicTrainingEffectMessage': 'IMPROVING_LACTATE_THRESHOLD_12',
            'anaerobicTrainingEffect': 2.0,
            'anaerobicTrainingEffectMessage': 'MAINTAINING_ANAEROBIC_BASE_1',
            'atpActivity': False,
            'autoCalcCalories': False,
            'averageBikingCadenceInRevPerMinute': 84.0,
            'averageHR': 157.0,
            'averageSpeed': 6.916999816894531,
            'avgPower': 95.0,
            'beginTimestamp': 1736689561000,
            'calories': 575.0,
            'decoDive': False,
            'deviceId': 1,
            'distance': 24938.140625,
            'duration': 3600.0,
            'elapsedDuration': 3600.0,
            'elevationCorrected': False,
            'eventType': {
                'sortOrder': 10,
                'typeId': 9,
                'typeKey': 'uncategorized'
            },
            'excludeFromPowerCurveReports': False,
            'favorite': False,
            'hasHeatMap': False,
            'hasImages': False,
            'hasPolyline': False,
            'hasSplits': False,
            'hasVideo': False,
            'hrTimeInZone_0': 245.0,
            'hrTimeInZone_1': 0.0,
            'hrTimeInZone_2': 342.0,
            'hrTimeInZone_3': 1390.0,
            'hrTimeInZone_4': 1576.0,
            'hrTimeInZone_5': 45.0,
            'intensityFactor': 0.8435400592370058,
            'lapCount': 3,
            'manualActivity': False,
            'manufacturer': 'TACX',
            'max20MinPower': 103.88583333333334,
            'maxAvgPower_1': 212,
            'maxAvgPower_10': 196,
            'maxAvgPower_120': 147,
            'maxAvgPower_1200': 104,
            'maxAvgPower_1800': 101,
            'maxAvgPower_2': 209,
            'maxAvgPower_20': 192,
            'maxAvgPower_30': 188,
            'maxAvgPower_300': 121,
            'maxAvgPower_5': 197,
            'maxAvgPower_60': 183,
            'maxAvgPower_600': 112,
            'maxBikingCadenceInRevPerMinute': 122.0,
            'maxHR': 182.0,
            'maxPower': 219.0,
            'maxSpeed': 9.888999938964844,
            'minActivityLapDuration': 60.0,
            'movingDuration': 3598.0,
            'normPower': 111.34728781928477,
            'ownerDisplayName': 'd4af4b8f-2d8f-4115-9c9f-d1a51b94e9a0',
            'ownerFullName': 'Chloe',
            'ownerId': 97325604,
            'ownerProfileImageUrlLarge': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/46f4ba78-b078-4e96-b9e1-2004ddcf53d2-97325604.JPG',
            'ownerProfileImageUrlMedium': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/243dafa6-b835-4789-8c57-4df8516b3ec2-97325604.JPG',
            'ownerProfileImageUrlSmall': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/f82664f6-02c3-4a88-98f9-632b1876e9c5-97325604.JPG',
            'parent': False,
            'powerTimeInZone_0': 0.0,
            'powerTimeInZone_1': 2078.0,
            'powerTimeInZone_2': 1277.0,
            'powerTimeInZone_3': 174.0,
            'powerTimeInZone_4': 68.0,
            'powerTimeInZone_5': 1.0,
            'powerTimeInZone_6': 0.0,
            'powerTimeInZone_7': 0.0,
            'pr': False,
            'privacy': {
                'typeId': 2,
                'typeKey': 'private'
            },
            'purposeful': False,
            'splitSummaries': [],
            'sportTypeId': 2,
            'startTimeGMT': '2025-01-12 13:46:01',
            'startTimeLocal': '2025-01-12 08:46:01',
            'summarizedDiveInfo': {
                'summarizedDiveGases': []
            },
            'timeZoneId': 149,
            'trainingEffectLabel': 'LACTATE_THRESHOLD',
            'trainingStressScore': 71.15598315375713,
            'userPro': False,
            'userRoles': [
                'SCOPE_GOLF_API_READ',
                'SCOPE_ATP_READ',
                'SCOPE_DIVE_API_WRITE',
                'SCOPE_COMMUNITY_COURSE_ADMIN_READ',
                'SCOPE_DIVE_API_READ',
                'SCOPE_DI_OAUTH_2_CLIENT_READ',
                'SCOPE_CONNECT_WRITE',
                'SCOPE_COMMUNITY_COURSE_WRITE',
                'SCOPE_MESSAGE_GENERATION_READ',
                'SCOPE_DI_OAUTH_2_CLIENT_REVOCATION_ADMIN',
                'SCOPE_CONNECT_WEB_TEMPLATE_RENDER',
                'SCOPE_OMT_SUBSCRIPTION_ADMIN_READ',
                'SCOPE_CONNECT_NON_SOCIAL_SHARED_READ',
                'SCOPE_CONNECT_READ',
                'SCOPE_DI_OAUTH_2_TOKEN_ADMIN',
                'ROLE_CONNECTUSER',
                'ROLE_FITNESS_USER',
                'ROLE_WELLNESS_USER'
            ]
        },
        {
            'activityId': 17978761786,
            'activityName': '10 min Full Body Stretch with Rebecca Kennedy',
            'activityType': {
                'isHidden': False,
                'parentTypeId': 29,
                'restricted': False,
                'trimmable': False,
                'typeId': 13,
                'typeKey': 'strength_training'
            },
            'atpActivity': False,
            'autoCalcCalories': False,
            'averageHR': 0.0,
            'averageRunningCadenceInStepsPerMinute': 0.0,
            'averageSpeed': 0.0,
            'avgPower': 0.0,
            'beginTimestamp': 1736656621000,
            'calories': 33.0,
            'decoDive': False,
            'deviceId': 1,
            'distance': 0.0,
            'duration': 600.0,
            'elapsedDuration': 600.0,
            'elevationCorrected': False,
            'eventType': {
                'sortOrder': 10,
                'typeId': 9,
                'typeKey': 'uncategorized'
            },
            'favorite': False,
            'hasHeatMap': False,
            'hasImages': False,
            'hasPolyline': False,
            'hasSplits': False,
            'hasVideo': False,
            'lapCount': 1,
            'manualActivity': False,
            'manufacturer': 'GARMIN',
            'maxDoubleCadence': 0.0,
            'maxHR': 0.0,
            'maxPower': 0.0,
            'maxRunningCadenceInStepsPerMinute': 0.0,
            'maxSpeed': 0.0,
            'minActivityLapDuration': 600.0,
            'movingDuration': 0.0,
            'ownerDisplayName': 'd4af4b8f-2d8f-4115-9c9f-d1a51b94e9a0',
            'ownerFullName': 'Chloe',
            'ownerId': 97325604,
            'ownerProfileImageUrlLarge': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/46f4ba78-b078-4e96-b9e1-2004ddcf53d2-97325604.JPG',
            'ownerProfileImageUrlMedium': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/243dafa6-b835-4789-8c57-4df8516b3ec2-97325604.JPG',
            'ownerProfileImageUrlSmall': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/f82664f6-02c3-4a88-98f9-632b1876e9c5-97325604.JPG',
            'parent': False,
            'pr': False,
            'privacy': {
                'typeId': 2,
                'typeKey': 'private'
            },
            'purposeful': False,
            'splitSummaries': [],
            'sportTypeId': 4,
            'startTimeGMT': '2025-01-12 04:37:01',
            'startTimeLocal': '2025-01-11 23:37:01',
            'summarizedDiveInfo': {
                'summarizedDiveGases': []
            },
            'timeZoneId': 149,
            'userPro': False,
            'userRoles': [
                'SCOPE_GOLF_API_READ',
                'SCOPE_ATP_READ',
                'SCOPE_DIVE_API_WRITE',
                'SCOPE_COMMUNITY_COURSE_ADMIN_READ',
                'SCOPE_DIVE_API_READ',
                'SCOPE_DI_OAUTH_2_CLIENT_READ',
                'SCOPE_CONNECT_WRITE',
                'SCOPE_COMMUNITY_COURSE_WRITE',
                'SCOPE_MESSAGE_GENERATION_READ',
                'SCOPE_DI_OAUTH_2_CLIENT_REVOCATION_ADMIN',
                'SCOPE_CONNECT_WEB_TEMPLATE_RENDER',
                'SCOPE_OMT_SUBSCRIPTION_ADMIN_READ',
                'SCOPE_CONNECT_NON_SOCIAL_SHARED_READ',
                'SCOPE_CONNECT_READ',
                'SCOPE_DI_OAUTH_2_TOKEN_ADMIN',
                'ROLE_CONNECTUSER',
                'ROLE_FITNESS_USER',
                'ROLE_WELLNESS_USER'
            ]
        }
    ]


# endregion temp


if __name__ == '__main__':
    import os
    from garminconnect import Garmin
    from notion_client import Client

    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DB_ID")

    # Initialize API clients
    notion_client = Client(auth=notion_token)
    garmin_client = Garmin(garmin_email, garmin_password)
    garmin_client.login()

    # Validate Notion database
    notion_database = notion_client.databases.retrieve(database_id)
    parsed_database = NotionDatabase.model_validate(notion_database)
    # TODO:
    #  id_fields = []
    #  data_fields = []

    # get Garmin activities
    # garmin_activities = garmin_client.get_activities(0, 10)
    raw_garmin_activities = get_fake_activities()
    garmin_activities = (
        GarminActivity.model_validate(activity)
        for activity in raw_garmin_activities
    )

    assert 1
