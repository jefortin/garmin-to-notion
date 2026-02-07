from pydantic import BaseModel, AwareDatetime, HttpUrl, NonNegativeFloat


class TrainingEffect(BaseModel):
    score: NonNegativeFloat
    label: str


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
    avg_pace_min_km: NonNegativeFloat
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
            "Date": {"date": {"start": truncated_timestamp.isoformat()}},
            "Activity Type": {"select": {"name": self.type}},
            "Subactivity Type": {"select": {"name": self.subtype}},
            "Activity Name": {"title": [{"text": {"content": self.__formatted_activity_name}}]},
            "Distance (km)": {"number": round(self.distance_km, 2)},
            "Duration (min)": {"number": round(self.duration_minutes, 2)},
            "Calories": {"number": int(self.calories)},
            "Avg Pace": {"rich_text": [{"text": {"content": self.__pace_label}}]},
            "Avg Power": {"number": round(self.avg_power, 1)},
            "Max Power": {"number": round(self.max_power, 1)},
            "Training Effect": {"select": {"name": self.__training_message_label}},
            "Aerobic": {"number": round(self.aerobic_effect.score, 1)},
            "Aerobic Effect": {"select": {"name": self.__format_training_effect(self.aerobic_effect.label)}},
            "Anaerobic": {"number": round(self.anaerobic_effect.score, 1)},
            "Anaerobic Effect": {"select": {"name": self.__format_training_effect(self.anaerobic_effect.label)}},
            "PR": {"checkbox": self.is_personal_record},
            "Fav": {"checkbox": self.is_favorite}
        }

    @property
    def __formatted_activity_name(self) -> str:
        # Garmin's "Entertainment" activity type is often used for Netflix workouts.
        name = self.name.replace('ENTERTAINMENT', 'Netflix')

        return name

    @property
    def __pace_label(self) -> str:
        if self.avg_pace_min_km > 0:
            pace_min_km = self.avg_pace_min_km
            minutes = int(pace_min_km)
            seconds = int((pace_min_km - minutes) * 60)
            return f"{minutes}:{seconds:02d} min/km"

        # No pace data available.
        return ""

    @property
    def __training_message_label(self) -> str:
        return self.training_effect.replace('_', ' ').title()

    @staticmethod
    def __format_training_effect(message: str) -> str:
        messages = {
            'NO_': 'No Benefit',
            'MINOR_': 'Some Benefit',
            'RECOVERY_': 'Recovery',
            'MAINTAINING_': 'Maintaining',
            'IMPROVING_': 'Impacting',
            'IMPACTING_': 'Impacting',
            'HIGHLY_': 'Highly Impacting',
            'OVERREACHING_': 'Overreaching'
        }
        for key, value in messages.items():
            if message.startswith(key):
                return value
        return message
