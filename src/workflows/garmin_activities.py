from garminconnect import Garmin as GarminClient
from notion_client import Client as NotionClient

from garmin import GarminConfiguration, get_garmin_client, ActivityResponse, ActivityListResponse
from notion import NotionConfiguration, get_notion_client, NotionActivity
from workflows.configuration import WorkflowConfiguration, get_workflow_configuration


class GarminActivitySynchronizer:
    def __init__(
        self,
        workflow_configuration: WorkflowConfiguration,
        garmin_client: GarminClient,
        garmin_configuration: GarminConfiguration,
        notion_client: NotionClient,
        notion_configuration: NotionConfiguration,
    ):
        self.__workflow_configuration = workflow_configuration
        self.__garmin_client = garmin_client
        self.__garmin_configuration = garmin_configuration
        self.__notion_client = notion_client
        self.__notion_configuration = notion_configuration

    def __get_activities(self) -> list[ActivityResponse]:
        return ActivityListResponse.validate_python(
            self.__garmin_client.get_activities(
                start=0,
                limit=self.__garmin_configuration.activity_fetch_limit
            )
        )

    def __activity_exists(self, notion_activity: NotionActivity) -> dict | None:
        query = self.__notion_client.databases.query(
            database_id=self.__notion_configuration.activities_database_id,
            filter=notion_activity.to_notion_lookup(),
        )
        results = query['results']
        return results[0] if results else None

    @staticmethod
    def __activity_needs_update(existing_page: dict, new_activity: NotionActivity):
        page_notion_activity = NotionActivity.from_notion_page(existing_page)

        # Compare the formatted properties because:
        # - Some modifications can occur during formating (e.g. number rounding, text casing, etc.)
        # - This is essentially what we want in the Notion page. If the formatted properties is not what we want, we
        #   need to update even if the underlying values are the same.
        return new_activity.to_notion_properties() == page_notion_activity.to_notion_properties()

    def __create_activity(self, notion_activity: NotionActivity) -> None:
        if self.__workflow_configuration.is_dry_run:
            print(f"Would create activity with data: {notion_activity.model_dump()}")
            return

        icon_url = notion_activity.icon_url
        properties = notion_activity.to_notion_properties()

        page = {
            "parent": {"database_id": self.__notion_configuration.activities_database_id},
            "properties": properties,
        }

        if icon_url:
            page["icon"] = {"type": "external", "external": {"url": icon_url}}

        self.__notion_client.pages.create(**page)
        print(f"Created: {notion_activity.type} - {notion_activity.name}")

    def __update_activity(self, existing_activity: dict, new_activity: NotionActivity) -> None:
        existing_activity_id = existing_activity['id']

        if self.__workflow_configuration.is_dry_run:
            print(f"Would update activity '{existing_activity_id}' with new data: {new_activity.model_dump()}")
            return

        icon_url = new_activity.icon_url
        properties = new_activity.to_notion_properties()

        update = {
            "page_id": existing_activity_id,
            "properties": properties,
        }

        if icon_url:
            update["icon"] = {"type": "external", "external": {"url": icon_url}}

        self.__notion_client.pages.update(**update)
        print(f"Updated: {new_activity.type} - {new_activity.name} #{existing_activity_id}")

    def synchronize_activities(self):
        """
        Sync a single Garmin activity to Notion.
        - Creates a new activity if it doesn't exist in Notion.
        - Updates the activity if it already exists in Notion but the existing data doesn't match the received data.
        - Does nothing if the activity already exists in Notion and the existing data matches the received data.
        """
        activities = self.__get_activities()

        for activity in activities:
            notion_activity = activity.to_notion_activity()
            existing_activity = self.__activity_exists(notion_activity)

            if existing_activity:
                if self.__activity_needs_update(existing_activity, notion_activity):
                    self.__update_activity(existing_activity, notion_activity)
            else:
                self.__create_activity(notion_activity)


def main():
    workflow_configuration = get_workflow_configuration()
    garmin_client, garmin_configuration = get_garmin_client()
    notion_client, notion_configuration = get_notion_client()

    synchronizer = GarminActivitySynchronizer(
        workflow_configuration,
        garmin_client,
        garmin_configuration,
        notion_client,
        notion_configuration,
    )
    synchronizer.synchronize_activities()


if __name__ == '__main__':
    main()
