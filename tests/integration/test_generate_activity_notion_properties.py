from unittest.mock import Mock

from helpers import get_garmin_client
from models import ActivityResponse
from workflows.garmin_activities import create_activity


class TestGenerateActivityNotionProperties:
    def test_activity_property_migration(self):
        def get_old_properties(garmin_activity: dict) -> dict:
            notion_client_mock = Mock()
            create_activity(notion_client_mock, "some_database_id", garmin_activity)

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
