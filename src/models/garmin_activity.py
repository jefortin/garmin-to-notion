from datetime import datetime, UTC
from typing import List

from pydantic import BaseModel, SecretStr, HttpUrl, TypeAdapter

from .notion_activity import NotionActivity, TrainingEffect, TrainingEffectLabel, PaceMinKm

ACTIVITY_ICONS: dict[str, HttpUrl] = {
    "Barre": HttpUrl("https://img.icons8.com/?size=100&id=66924&format=png&color=000000"),
    "Breathwork": HttpUrl("https://img.icons8.com/?size=100&id=9798&format=png&color=000000"),
    "Cardio": HttpUrl("https://img.icons8.com/?size=100&id=71221&format=png&color=000000"),
    "Cycling": HttpUrl("https://img.icons8.com/?size=100&id=47443&format=png&color=000000"),
    "Hiking": HttpUrl("https://img.icons8.com/?size=100&id=9844&format=png&color=000000"),
    "Indoor Cardio": HttpUrl("https://img.icons8.com/?size=100&id=62779&format=png&color=000000"),
    "Indoor Cycling": HttpUrl("https://img.icons8.com/?size=100&id=47443&format=png&color=000000"),
    "Indoor Rowing": HttpUrl("https://img.icons8.com/?size=100&id=71098&format=png&color=000000"),
    "Pilates": HttpUrl("https://img.icons8.com/?size=100&id=9774&format=png&color=000000"),
    "Meditation": HttpUrl("https://img.icons8.com/?size=100&id=9798&format=png&color=000000"),
    "Rowing": HttpUrl("https://img.icons8.com/?size=100&id=71491&format=png&color=000000"),
    "Running": HttpUrl("https://img.icons8.com/?size=100&id=k1l1XFkME39t&format=png&color=000000"),
    "Strength Training": HttpUrl("https://img.icons8.com/?size=100&id=107640&format=png&color=000000"),
    "Stretching": HttpUrl("https://img.icons8.com/?size=100&id=djfOcRn1m_kh&format=png&color=000000"),
    "Swimming": HttpUrl("https://img.icons8.com/?size=100&id=9777&format=png&color=000000"),
    "Treadmill Running": HttpUrl("https://img.icons8.com/?size=100&id=9794&format=png&color=000000"),
    "Walking": HttpUrl("https://img.icons8.com/?size=100&id=9807&format=png&color=000000"),
    "Yoga": HttpUrl("https://img.icons8.com/?size=100&id=9783&format=png&color=000000"),
    # Add more mappings as needed
}


class ActivityType(BaseModel):
    isHidden: bool
    parentTypeId: int
    restricted: bool
    trimmable: bool
    typeId: int
    typeKey: str


class EventType(BaseModel):
    sortOrder: int
    typeId: int
    typeKey: str


class Privacy(BaseModel):
    typeId: int
    typeKey: str


class SummarizedDiveInfo(BaseModel):
    """
    TODO: Not supported yet - Unknown structure based on observed data.
    """
    pass


class SplitSummary(BaseModel):
    averageSpeed: float
    distance: float
    duration: float
    maxDistance: float
    maxSpeed: float | None = None  # Seems to be missing when avg speed is 0.
    numClimbSends: int
    numFalls: int
    splitType: str  # Could probably use an enum: 'INTERVAL_ACTIVE' | 'INTERVAL_REST' | ???


class SummarizedExerciseSet(BaseModel):
    category: str
    duration: float
    maxWeight: int | None = None  # Not all sets have weight data, e.g. bodyweight exercises
    reps: int
    sets: int
    subCategory: str | None = None
    volume: int


class ActivityResponse(BaseModel):
    """
    This model represents the structure of activity data returned from Garmin Connect API.
    Some fields are optional as they don't appear in all activity types.

    TODO: This model is still incomplete. Update as needed to support more activity fields.
    """

    # Core activity identifiers
    activityId: int
    activityName: str
    activityUUID: str

    # Activity type and classification
    activityType: ActivityType
    sportTypeId: int
    eventType: EventType

    # Optional - training metrics
    activityTrainingLoad: float | None = None
    aerobicTrainingEffect: float | None = None
    aerobicTrainingEffectMessage: str | None = None
    anaerobicTrainingEffect: float | None = None
    anaerobicTrainingEffectMessage: str | None = None
    trainingEffectLabel: str | None = None

    # Activity flags and settings
    atpActivity: bool
    autoCalcCalories: bool
    decoDive: bool
    elevationCorrected: bool
    favorite: bool
    hasHeatMap: bool
    hasImages: bool
    hasPolyline: bool
    hasSplits: bool
    hasVideo: bool
    manualActivity: bool
    parent: bool
    pr: bool
    purposeful: bool
    qualifyingDive: bool
    userPro: bool

    # Metrics and measurements
    maxRunningCadenceInStepsPerMinute: float | None = None
    maxDoubleCadence: float | None = None
    averageRunningCadenceInStepsPerMinute: float | None = None
    averageSpeed: float
    calories: float
    distance: float
    duration: float
    elapsedDuration: float
    avgPower: float | None = None
    maxPower: float | None = None
    maxSpeed: float | None = None
    minActivityLapDuration: float
    movingDuration: float

    # Optional - Heart rate zones (present in activities with HR monitoring)
    averageHR: float | None = None
    maxHR: float | None = None
    hrTimeInZone_1: float | None = None
    hrTimeInZone_2: float | None = None
    hrTimeInZone_3: float | None = None
    hrTimeInZone_4: float | None = None
    hrTimeInZone_5: float | None = None

    # Timestamps and timing
    beginTimestamp: int
    endTimeGMT: str
    startTimeGMT: str
    startTimeLocal: str
    timeZoneId: int

    # Device and manufacturer info
    deviceId: int
    manufacturer: str

    # Activity structure
    lapCount: int

    # Owner/user information
    ownerDisplayName: SecretStr
    ownerFullName: SecretStr
    ownerId: int
    ownerProfileImageUrlLarge: SecretStr
    ownerProfileImageUrlMedium: SecretStr
    ownerProfileImageUrlSmall: SecretStr

    # Privacy and permissions
    privacy: Privacy
    userRoles: List[str]

    # Activity data containers
    splitSummaries: List[SplitSummary]
    summarizedDiveInfo: SummarizedDiveInfo

    # Optional - Strength training fields
    activeSets: int | None = None
    summarizedExerciseSets: List[SummarizedExerciseSet] | None = None
    totalReps: int | None = None
    totalSets: int | None = None

    class Config:
        frozen = True
        # Allow extra fields for forward compatibility
        extra = "allow"
        use_enum_values = True
        validate_assignment = True

    @property
    def __activity_type_tuple(self) -> tuple[str, str]:
        # Overrides based on activity name keywords. This is opinionated and could be adjusted based on user
        # preferences or additional activity types.
        if 'meditation' in self.activityName.lower():
            return "Meditation", "Meditation"
        if "barre" in self.activityName.lower():
            return "Strength", "Barre"
        if "stretch" in self.activityName.lower():
            return "Stretching", "Stretching"

        sanitized_type_key = (
            self.activityType.typeKey
            .replace('_v2', '')  # strip version suffixes, e.g. "rowing_v2" -> "rowing"
            .replace('_', ' ')
            .strip()
            .title()
        )

        # Initialize subtype as the same as the main type
        activity_subtype = sanitized_type_key

        # Custom mapping for base activity types.
        activity_mapping = {
            "Barre": "Strength",
            "Indoor Cardio": "Cardio",
            "Indoor Cycling": "Cycling",
            "Indoor Rowing": "Rowing",
            "Speed Walking": "Walking",
            "Strength Training": "Strength",
            "Treadmill Running": "Running",
            # Custom grouping for similar mind-body activities.
            "Yoga": "Yoga/Pilates",
            "Pilates": "Yoga/Pilates"
        }
        # Use the custom mapping if one exists, otherwise fall back to the sanitized type key
        activity_type = activity_mapping.get(sanitized_type_key, sanitized_type_key)

        # If the formatted type is in our mapping, update both main type and subtype
        if sanitized_type_key in activity_mapping:
            activity_type = activity_mapping[sanitized_type_key]

        return activity_type, activity_subtype

    def to_notion_activity(self) -> NotionActivity:
        """
        Converts the ActivityResponse instance into a NotionActivity instance.
        This method maps relevant fields from the Garmin activity data to the structure expected by Notion.
        """
        parsed_timestamp = (
            datetime
            .strptime(self.startTimeGMT, '%Y-%m-%d %H:%M:%S')  # Parse as format received from Garmin
            .replace(tzinfo=UTC)  # Set timezone to UTC, as Garmin times are in GMT/UTC. Close enough.
        )
        activity_type, activity_subtype = self.__activity_type_tuple
        icon_url = ACTIVITY_ICONS.get(activity_subtype)
        formatted_training_effect = (self.trainingEffectLabel or "Unknown").replace('_', ' ').title()
        # Garmin's "Entertainment" activity type is often used for Netflix workouts.
        formatted_activity_name = self.activityName.replace('ENTERTAINMENT', 'Netflix')

        pace_min_per_km = 1000 / (self.averageSpeed * 60) if self.averageSpeed > 0 else 0  # Convert to min/km

        return NotionActivity(
            timestamp=parsed_timestamp,
            name=formatted_activity_name,
            type=activity_type,
            subtype=activity_subtype,
            icon_url=icon_url,
            distance_km=self.distance / 1000,  # Convert meters to kilometers
            duration_minutes=self.duration / 60,  # Convert seconds to minutes
            calories=self.calories,
            avg_pace_min_km=PaceMinKm(pace_min_per_km=pace_min_per_km),
            avg_power=self.avgPower or 0,
            max_power=self.maxPower or 0,
            training_effect=formatted_training_effect,  # TODO: Use enum if we can get a list of possible values.
            aerobic_effect=TrainingEffect(
                score=self.aerobicTrainingEffect or 0,
                label=TrainingEffectLabel.UNKNOWN
                if not self.aerobicTrainingEffectMessage
                else TrainingEffectLabel.from_garmin_message(self.aerobicTrainingEffectMessage)
            ),
            anaerobic_effect=TrainingEffect(
                score=self.anaerobicTrainingEffect or 0,
                label=TrainingEffectLabel.UNKNOWN
                if not self.anaerobicTrainingEffectMessage
                else TrainingEffectLabel.from_garmin_message(self.anaerobicTrainingEffectMessage)
            ),
            is_personal_record=self.pr,
            is_favorite=self.favorite
        )


ActivityListResponse = TypeAdapter(list[ActivityResponse])
