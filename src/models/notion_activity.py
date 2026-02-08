from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, AwareDatetime, HttpUrl, NonNegativeFloat


class PaceMinKm(BaseModel):
    pace_min_per_km: NonNegativeFloat

    def to_string(self) -> str:
        if self.pace_min_per_km > 0:
            minutes = int(self.pace_min_per_km)
            seconds = int((self.pace_min_per_km - minutes) * 60)
            return f"{minutes}:{seconds:02d} min/km"
        return ""  # No pace data available.

    @classmethod
    def from_string(cls, pace_str: str) -> Self:
        try:
            minutes, seconds = map(int, pace_str.replace(" min/km", "").split(":"))
            pace_min_per_km = minutes + seconds / 60
        except ValueError:
            pace_min_per_km = 0.0  # Default to 0 if parsing fails

        return cls(pace_min_per_km=pace_min_per_km)


class TrainingEffectLabel(StrEnum):
    UNKNOWN = 'Unknown'
    NO_BENEFIT = 'No Benefit'
    SOME_BENEFIT = 'Some Benefit'
    RECOVERY = 'Recovery'
    MAINTAINING = 'Maintaining'
    IMPROVING = 'Impacting'
    IMPACTING = 'Impacting'
    HIGHLY_IMPACTING = 'Highly Impacting'
    OVERREACHING = 'Overreaching'

    @classmethod
    def from_garmin_message(cls, message: str) -> Self:
        messages = {
            'NO_': cls.NO_BENEFIT,
            'MINOR_': cls.SOME_BENEFIT,
            'RECOVERY_': cls.RECOVERY,
            'MAINTAINING_': cls.MAINTAINING,
            'IMPROVING_': cls.IMPROVING,
            'IMPACTING_': cls.IMPACTING,
            'HIGHLY_': cls.HIGHLY_IMPACTING,
            'OVERREACHING_': cls.OVERREACHING,
        }

        for prefix, label in messages.items():
            if message.startswith(prefix):
                return label

        return cls.UNKNOWN


class TrainingEffect(BaseModel):
    score: NonNegativeFloat
    label: TrainingEffectLabel


class NotionActivity(BaseModel):
    """
    Represents the structure of activity data that will be stored in Notion.
    """
    timestamp: AwareDatetime
    name: str
    type: str
    subtype: str
    icon_url: HttpUrl | None
    distance_km: NonNegativeFloat
    duration_minutes: NonNegativeFloat
    calories: NonNegativeFloat
    avg_pace_min_km: PaceMinKm
    avg_power: NonNegativeFloat
    max_power: NonNegativeFloat
    training_effect: str
    aerobic_effect: TrainingEffect
    anaerobic_effect: TrainingEffect
    is_personal_record: bool
    is_favorite: bool

    class Config:
        frozen = True

    def to_notion_properties(self) -> dict:
        """
        Converts the NotionActivity instance into a dictionary format suitable for Notion API.
        """
        truncated_timestamp = self.timestamp.replace(second=0, microsecond=0)  # Notion truncates to the minute.
        return {
            "Activity Name": {"title": [{"text": {"content": self.name}}]},
            "Date": {"date": {"start": truncated_timestamp.isoformat()}},
            "Activity Type": {"select": {"name": self.type}},
            "Subactivity Type": {"select": {"name": self.subtype}},
            "Distance (km)": {"number": round(self.distance_km, 2)},
            "Duration (min)": {"number": round(self.duration_minutes, 2)},
            "Calories": {"number": int(self.calories)},
            "Avg Pace": {"rich_text": [{"text": {"content": self.avg_pace_min_km.to_string()}}]},
            "Avg Power": {"number": round(self.avg_power, 1)},
            "Max Power": {"number": round(self.max_power, 1)},
            "Training Effect": {"select": {"name": self.training_effect}},
            "Aerobic": {"number": round(self.aerobic_effect.score, 1)},
            "Aerobic Effect": {"select": {"name": str(self.aerobic_effect.label)}},
            "Anaerobic": {"number": round(self.anaerobic_effect.score, 1)},
            "Anaerobic Effect": {"select": {"name": str(self.anaerobic_effect.label)}},
            "PR": {"checkbox": self.is_personal_record},
            "Fav": {"checkbox": self.is_favorite}
        }

    @classmethod
    def from_notion_page(cls, notion_page: dict):
        """
        Creates a NotionActivity instance from a Notion page data.
        Assumes the data is in the same format as produced by to_notion_properties. If unexpected formats are
        encountered, this will throw.
        """
        icon_url = notion_page['icon']['external']['url']

        properties = notion_page.get('properties', {})
        return cls(
            timestamp=datetime.fromisoformat(properties['Date']['date']['start']),
            name=properties['Activity Name']['title'][0]['text']['content'],
            type=properties['Activity Type']['select']['name'],
            subtype=properties['Subactivity Type']['select']['name'],
            icon_url=icon_url,
            distance_km=properties['Distance (km)']['number'],
            duration_minutes=properties['Duration (min)']['number'],
            calories=properties['Calories']['number'],
            avg_pace_min_km=PaceMinKm.from_string(properties['Avg Pace']['rich_text'][0]['text']['content']),
            avg_power=properties['Avg Power']['number'],
            max_power=properties['Max Power']['number'],
            training_effect=properties['Training Effect']['select']['name'],
            aerobic_effect=TrainingEffect(
                score=properties['Aerobic']['number'],
                label=TrainingEffectLabel.from_garmin_message(properties['Aerobic Effect']['select']['name'])
            ),
            anaerobic_effect=TrainingEffect(
                score=properties['Anaerobic']['number'],
                label=TrainingEffectLabel.from_garmin_message(properties['Anaerobic Effect']['select']['name'])
            ),
            is_personal_record=properties['PR']['checkbox'],
            is_favorite=properties['Fav']['checkbox']
        )

    def to_notion_lookup(self):
        """
        Generates a filter dictionary for searching for this activity in Notion.
        # TODO: We should store the activity ID in the Notion page to avoid unreliable lookups. Needs a migration plan.
        """
        truncated_timestamp = self.timestamp.replace(second=0, microsecond=0)  # Notion truncates to the minute.
        return {
            "and": [
                {"property": "Date", "date": {"equals": truncated_timestamp.isoformat()}},
                {"property": "Activity Type", "select": {"equals": self.type}},
                {"property": "Activity Name", "title": {"equals": self.name}}
            ]
        }
