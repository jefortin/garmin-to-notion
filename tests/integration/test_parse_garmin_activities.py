from helpers import get_garmin_client
from models import ActivityResponse


class TestParseGarminActivities:
    def test_parse_fetched_garmin_activities(self):
        """
        Uses the actual activity fetch flow and checks that all fetched activities can be parsed into the
        ActivityResponse model without errors.

        Run this to diagnose any parsing issues.
        """

        garmin_client, garmin_configuration = get_garmin_client()
        activities = garmin_client.get_activities(0, garmin_configuration.activity_fetch_limit)

        for activity in activities:
            try:
                assert ActivityResponse.model_validate(activity)
            except Exception as e:
                assert False, f"Failed to parse activity data [{activity}]: {str(e)}"
