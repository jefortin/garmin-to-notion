from unittest.mock import Mock

from notion_client import Client as NotionClient

from helpers import get_garmin_client
from models import ActivityResponse


class _LegacyGarminActivities:
    ACTIVITY_ICONS = {
        "Barre": "https://img.icons8.com/?size=100&id=66924&format=png&color=000000",
        "Breathwork": "https://img.icons8.com/?size=100&id=9798&format=png&color=000000",
        "Cardio": "https://img.icons8.com/?size=100&id=71221&format=png&color=000000",
        "Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=000000",
        "Hiking": "https://img.icons8.com/?size=100&id=9844&format=png&color=000000",
        "Indoor Cardio": "https://img.icons8.com/?size=100&id=62779&format=png&color=000000",
        "Indoor Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=000000",
        "Indoor Rowing": "https://img.icons8.com/?size=100&id=71098&format=png&color=000000",
        "Pilates": "https://img.icons8.com/?size=100&id=9774&format=png&color=000000",
        "Meditation": "https://img.icons8.com/?size=100&id=9798&format=png&color=000000",
        "Rowing": "https://img.icons8.com/?size=100&id=71491&format=png&color=000000",
        "Running": "https://img.icons8.com/?size=100&id=k1l1XFkME39t&format=png&color=000000",
        "Strength Training": "https://img.icons8.com/?size=100&id=107640&format=png&color=000000",
        "Stretching": "https://img.icons8.com/?size=100&id=djfOcRn1m_kh&format=png&color=000000",
        "Swimming": "https://img.icons8.com/?size=100&id=9777&format=png&color=000000",
        "Treadmill Running": "https://img.icons8.com/?size=100&id=9794&format=png&color=000000",
        "Walking": "https://img.icons8.com/?size=100&id=9807&format=png&color=000000",
        "Yoga": "https://img.icons8.com/?size=100&id=9783&format=png&color=000000",
        # Add more mappings as needed
    }

    @staticmethod
    def format_entertainment(activity_name: str) -> str:
        return activity_name.replace('ENTERTAINMENT', 'Netflix')

    @staticmethod
    def format_training_effect(training_effect_label: str) -> str:
        return training_effect_label.replace('_', ' ').title()

    @staticmethod
    def format_training_message(message: str) -> str:
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

    @staticmethod
    def format_pace(average_speed: float) -> str:
        if average_speed > 0:
            pace_min_km = 1000 / (average_speed * 60)  # Convert to min/km
            minutes = int(pace_min_km)
            seconds = int((pace_min_km - minutes) * 60)
            return f"{minutes}:{seconds:02d} min/km"
        else:
            return ""

    @staticmethod
    def format_activity_type(activity_type: str, activity_name: str = "") -> tuple[str, str]:
        # First format the activity type as before
        formatted_type = activity_type.replace('_', ' ').title() if activity_type else "Unknown"

        # Initialize subtype as the same as the main type
        activity_subtype = formatted_type
        activity_type = formatted_type

        # Map of specific subtypes to their main types
        activity_mapping = {
            "Barre": "Strength",
            "Indoor Cardio": "Cardio",
            "Indoor Cycling": "Cycling",
            "Indoor Rowing": "Rowing",
            "Speed Walking": "Walking",
            "Strength Training": "Strength",
            "Treadmill Running": "Running"
        }

        # Special replacement for Rowing V2
        if formatted_type == "Rowing V2":
            activity_type = "Rowing"

        # Special case for Yoga and Pilates
        elif formatted_type in ["Yoga", "Pilates"]:
            activity_type = "Yoga/Pilates"
            activity_subtype = formatted_type

        # If the formatted type is in our mapping, update both main type and subtype
        if formatted_type in activity_mapping:
            activity_type = activity_mapping[formatted_type]
            activity_subtype = formatted_type

        # Special cases for activity names
        if activity_name and "meditation" in activity_name.lower():
            return "Meditation", "Meditation"
        if activity_name and "barre" in activity_name.lower():
            return "Strength", "Barre"
        if activity_name and "stretch" in activity_name.lower():
            return "Stretching", "Stretching"

        return activity_type, activity_subtype

    @classmethod
    def create_activity(cls, notion_client: NotionClient, database_id: str, activity: dict) -> None:
        """
        Create activity method as implemented in the first iteration of the project.
        """
        if not isinstance(notion_client, Mock):
            # Sanity check to ensure we don't insert test data into a real Notion database during testing.
            raise ValueError("This method is only intended to be used with a Mock Notion client for testing purposes.")

        # Create a new activity in the Notion database
        activity_date = activity.get('startTimeGMT')
        activity_name = cls.format_entertainment(activity.get('activityName', 'Unnamed Activity'))
        activity_type, activity_subtype = cls.format_activity_type(
            activity.get('activityType', {}).get('typeKey', 'Unknown'),
            activity_name
        )

        # Get icon for the activity type
        icon_url = cls.ACTIVITY_ICONS.get(activity_subtype if activity_subtype != activity_type else activity_type)

        properties = {
            "Date": {"date": {"start": activity_date}},
            "Activity Type": {"select": {"name": activity_type}},
            "Subactivity Type": {"select": {"name": activity_subtype}},
            "Activity Name": {"title": [{"text": {"content": activity_name}}]},
            "Distance (km)": {"number": round(activity.get('distance', 0.0) / 1000, 2)},
            "Duration (min)": {"number": round(activity.get('duration', 0.0) / 60, 2)},
            "Calories": {"number": round(activity.get('calories', 0.0))},
            "Avg Pace": {"rich_text": [{"text": {"content": cls.format_pace(activity.get('averageSpeed', 0.0))}}]},
            "Avg Power": {"number": round(activity.get('avgPower', 0.0), 1)},
            "Max Power": {"number": round(activity.get('maxPower', 0.0), 1)},
            "Training Effect": {
                "select": {"name": cls.format_training_effect(activity.get('trainingEffectLabel', 'Unknown'))}
            },
            "Aerobic": {"number": round(activity.get('aerobicTrainingEffect', 0.0), 1)},
            "Aerobic Effect": {
                "select": {"name": cls.format_training_message(activity.get('aerobicTrainingEffectMessage', 'Unknown'))}
            },
            "Anaerobic": {"number": round(activity.get('anaerobicTrainingEffect', 0.0), 1)},
            "Anaerobic Effect": {
                "select": {
                    "name": cls.format_training_message(activity.get('anaerobicTrainingEffectMessage', 'Unknown'))
                }
            },
            "PR": {"checkbox": activity.get('pr', False)},
            "Fav": {"checkbox": activity.get('favorite', False)}
        }

        page = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }

        if icon_url:
            page["icon"] = {"type": "external", "external": {"url": icon_url}}

        notion_client.pages.create(**page)


class TestGenerateActivityNotionProperties:

    def test_activity_property_migration(self):
        """
        Compares the results of the old property generation method (directly in create_activity) with the new method
        for all fetched activities.
        The logic for comparing dates is different in that the new logic truncates to the minute (Notion's format)
        while the old logic may include seconds, but required workarounds when searching and comparing Notion pages.
        """

        def get_old_properties(garmin_activity: dict) -> dict:
            notion_client_mock = Mock()
            _LegacyGarminActivities.create_activity(notion_client_mock, "some_database_id", garmin_activity)

            return notion_client_mock.pages.create.call_args.kwargs['properties']

        def get_new_properties(garmin_activity: dict) -> dict:
            parsed = ActivityResponse.model_validate(garmin_activity)
            notion_activity = ActivityResponse.to_notion_activity(parsed)

            return notion_activity.to_notion_properties()

        garmin_client, garmin_configuration = get_garmin_client()
        activities = garmin_client.get_activities(0, garmin_configuration.activity_fetch_limit)

        for activity in activities:
            try:
                old_properties = get_old_properties(activity)
                old_datetime = old_properties.pop('Date')
                new_properties = get_new_properties(activity)
                new_datetime = new_properties.pop('Date')
            except Exception as e:
                assert False, f"Error processing activity with data [{activity}]: {e}"

            assert old_properties == new_properties
            # check that dates are the same after truncation to the minute (Notion's format)
            assert old_datetime['date']['start'][:16].replace('T', ' ') == new_datetime['date']['start'][:16].replace(
                'T',
                ' '
            )
