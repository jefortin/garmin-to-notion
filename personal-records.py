from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from functools import cached_property
from typing import Tuple, Optional, Annotated

from garminconnect import Garmin
from notion_client import Client
import os

from pydantic import BaseModel, HttpUrl, Field, NaiveDatetime, BeforeValidator, computed_field, AwareDatetime
from pydantic.experimental.pipeline import validate_as

from _distance import DistanceUnit, Distance
from _pace import Pace
from _time import TimeUnit, Duration, DurationFormat


class PersonalRecordDetails(BaseModel):
    """
    Generator for a personal record details.
    """

    category: str
    icon: str
    cover: HttpUrl
    # The type of the value depends on the activity type. String is sufficient for now.
    value_processor: Callable[[float], str]
    # Pace is not provided, but it can be calculated from the value of some activities.
    pace_processor: Callable[[float], str | None]


class PersonalRecordType(Enum):
    """
    Enum representing the different personal record activity types.
    TODO: This is probably not complete but I couldn't find the documentation on all the possible types.
    """

    RUN_1K = 1
    RUN_1MI = 2
    RUN_5K = 3
    RUN_10K = 4
    HALF_MARATHON = 5
    MARATHON = 6
    LONGEST_RUN = 7
    LONGEST_RIDE = 8
    TOTAL_ASCENT = 9
    MAX_AVG_POWER_20_MIN = 10
    RIDE_100_MI = 11
    MOST_STEPS_IN_A_DAY = 12
    MOST_STEPS_IN_A_WEEK = 13
    MOST_STEPS_IN_A_MONTH = 14
    LONGEST_GOAL_STREAK = 15

    __activity_details: dict[PersonalRecordType, PersonalRecordDetails] = {
        RUN_1K: PersonalRecordDetails(
            category="1K",
            icon="🥇",
            cover="https://images.unsplash.com/photo-1526676537331-7747bf8278fc?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: Duration(seconds=value).format(DurationFormat.M_S),
            pace_processor=lambda value: str(Pace(value, TimeUnit.SECOND, DistanceUnit.KILOMETER)),
        ),
        RUN_1MI: PersonalRecordDetails(
            category="1mi",
            icon="⚡",
            cover="https://images.unsplash.com/photo-1638183395699-2c0db5b6afbb?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: Duration(seconds=value).format(DurationFormat.M_S),
            pace_processor=lambda value: str(Pace(value, TimeUnit.SECOND, DistanceUnit.MILE)),
        ),
        RUN_5K: PersonalRecordDetails(
            category="5K",
            icon="👟",
            cover="https://images.unsplash.com/photo-1571008887538-b36bb32f4571?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: Duration(seconds=value).format(DurationFormat.M_S),
            pace_processor=lambda value: str(Pace(value / 5, TimeUnit.SECOND, DistanceUnit.KILOMETER)),
        ),
        RUN_10K: PersonalRecordDetails(
            category="10K",
            icon="⭐",
            cover="https://images.unsplash.com/photo-1529339944280-1a37d3d6fa8c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: Duration(seconds=value).format(DurationFormat.Dynamic),
            pace_processor=lambda value: str(Pace(value / 10, TimeUnit.SECOND, DistanceUnit.KILOMETER)),
        ),
        # HALF_MARATHON : ...
        # MARATHON: ...
        LONGEST_RUN: PersonalRecordDetails(
            category="Longest Run",
            icon="🏃",
            cover="https://images.unsplash.com/photo-1532383282788-19b341e3c422?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: str(Distance(value, DistanceUnit.METER).convert_to(DistanceUnit.KILOMETER)),
            pace_processor=lambda _: None,
        ),
        LONGEST_RIDE: PersonalRecordDetails(
            category="Longest Ride",
            icon="🚴",
            cover="https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: str(Distance(value, DistanceUnit.METER).convert_to(DistanceUnit.KILOMETER)),
            pace_processor=lambda _: None,
        ),
        TOTAL_ASCENT: PersonalRecordDetails(
            category="Total Ascent",
            icon="🚵",
            cover="https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: str(Distance(value, DistanceUnit.METER)),
            pace_processor=lambda _: None,
        ),
        MAX_AVG_POWER_20_MIN: PersonalRecordDetails(
            category="Max Avg Power (20 min)",
            icon="🔋",
            cover="https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: f"{round(value):,} W",
            pace_processor=lambda _: None,
        ),
        # RIDE_100_MI: ...
        MOST_STEPS_IN_A_DAY: PersonalRecordDetails(
            category="Most Steps in a Day",
            icon="👣",
            cover="https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: f"{round(value):,}",
            pace_processor=lambda _: None,
        ),
        MOST_STEPS_IN_A_WEEK: PersonalRecordDetails(
            category="Most Steps in a Week",
            icon="🚶",
            cover="https://images.unsplash.com/photo-1602174865963-9159ed37e8f1?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: f"{round(value):,}",
            pace_processor=lambda _: None,
        ),
        MOST_STEPS_IN_A_MONTH: PersonalRecordDetails(
            category="Most Steps in a Month",
            icon="📅",
            cover="https://images.unsplash.com/photo-1580058572462-98e2c0e0e2f0?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: f"{round(value):,}",
            pace_processor=lambda _: None,
        ),
        LONGEST_GOAL_STREAK: PersonalRecordDetails(
            category="Longest Goal Streak",
            icon="✔️",
            cover="https://images.unsplash.com/photo-1477332552946-cfb384aeaf1c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: f"{round(value)} days",
            pace_processor=lambda _: None,
        ),
    }

    def get_activity_details(self) -> PersonalRecordDetails:
        self.__activity_details: dict[PersonalRecordType, PersonalRecordDetails]
        return self.__activity_details.get(
            self,
            PersonalRecordDetails(
                category="Unnamed Activity",
                icon="🏅",
                cover="https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
                value_processor=lambda value: str(Duration(seconds=value)),
                pace_processor=lambda _: None,
            ),
        )


# region custom fields

def parse_naive_gmt_datetime(naive_gmt_datetime: datetime) -> datetime:
    if (naive_gmt_datetime.tzinfo is None) or (naive_gmt_datetime.tzinfo.utcoffset(naive_gmt_datetime) is None):
        return naive_gmt_datetime.replace(tzinfo=timezone.utc)

    return naive_gmt_datetime


def parse_activity_type_name(activity_type_name: str):
    if activity_type_name is None:
        return "Walking"

    return activity_type_name.replace('_', ' ').title()


def parse_personal_record_type(type_id: int) -> PersonalRecordDetails:
    try:
        return PersonalRecordType(type_id).get_activity_details()
    except ValueError:
        return PersonalRecordDetails(
            category="Unnamed Activity",
            icon="🏅",
            cover="https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
            value_processor=lambda value: str(Duration(seconds=value)),  # TODO: Is duration ok? Could be anything.
            pace_processor=lambda _: None,
        )


GmtDateTimeField = Annotated[datetime, validate_as(NaiveDatetime).transform(parse_naive_gmt_datetime)]
ActivityTypeField = Annotated[str, validate_as(Optional[str]).transform(parse_activity_type_name)]
PersonalRecordDetailsField = Annotated[PersonalRecordDetails, validate_as(int).transform(parse_personal_record_type)]


# endregion custom fields

class PersonalRecord(BaseModel):
    start_time: GmtDateTimeField = Field(..., validation_alias='prStartTimeGmtFormatted')
    activity_category: ActivityTypeField = Field(..., validation_alias='activityType')
    personal_record: PersonalRecordDetailsField = Field(..., validation_alias='typeId')

    # TODO: The value here is the raw value. We should ideally parse it immediately instead of using a generator, but
    #  this logic relies on 2 fields, and I'm not sure how to handle this in Pydantic yet.
    raw_value: float = Field(..., validation_alias='value')

    @computed_field
    @cached_property
    def value(self) -> str:
        return self.personal_record.value_processor(self.raw_value)

    @computed_field
    @cached_property
    def pace(self) -> str | None:
        return self.personal_record.pace_processor(self.raw_value)


def get_icon_for_record(activity_name):
    icon_map = {
        "1K": "🥇",
        "1mi": "⚡",
        "5K": "👟",
        "10K": "⭐",
        "Longest Run": "🏃",
        "Longest Ride": "🚴",
        "Total Ascent": "🚵",
        "Max Avg Power (20 min)": "🔋",
        "Most Steps in a Day": "👣",
        "Most Steps in a Week": "🚶",
        "Most Steps in a Month": "📅",
        "Longest Goal Streak": "✔️",
        "Other": "🏅"
    }
    return icon_map.get(activity_name, "🏅")  # Default to "Other" icon if not found


def get_cover_for_record(activity_name):
    cover_map = {
        "1K": "https://images.unsplash.com/photo-1526676537331-7747bf8278fc?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "1mi": "https://images.unsplash.com/photo-1638183395699-2c0db5b6afbb?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "5K": "https://images.unsplash.com/photo-1571008887538-b36bb32f4571?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "10K": "https://images.unsplash.com/photo-1529339944280-1a37d3d6fa8c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Run": "https://images.unsplash.com/photo-1532383282788-19b341e3c422?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Ride": "https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Max Avg Power (20 min)": "https://images.unsplash.com/photo-1591741535018-d042766c62eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2MzkyMXwwfDF8c2VhcmNofDJ8fHNwaW5uaW5nfGVufDB8fHx8MTcyNjM1Mzc0Mnww&ixlib=rb-4.0.3&q=80&w=4800",
        "Most Steps in a Day": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Most Steps in a Week": "https://images.unsplash.com/photo-1602174865963-9159ed37e8f1?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Most Steps in a Month": "https://images.unsplash.com/photo-1580058572462-98e2c0e0e2f0?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800",
        "Longest Goal Streak": "https://images.unsplash.com/photo-1477332552946-cfb384aeaf1c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800"
    }
    return cover_map.get(activity_name,
                         "https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=4800")



def get_existing_record(client, database_id, activity_name):
    query = client.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Record", "title": {"equals": activity_name}},
                {"property": "PR", "checkbox": {"equals": True}}
            ]
        }
    )
    return query['results'][0] if query['results'] else None


def get_record_by_date_and_name(client, database_id, activity_date, activity_name):
    query = client.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Record", "title": {"equals": activity_name}},
                {"property": "Date", "date": {"equals": activity_date}}
            ]
        }
    )
    return query['results'][0] if query['results'] else None


def update_record(client, page_id, activity_date, value, pace, activity_name, is_pr=True):
    properties = {
        "Date": {"date": {"start": activity_date}},
        "PR": {"checkbox": is_pr}
    }

    if value:
        properties["Value"] = {"rich_text": [{"text": {"content": value}}]}

    if pace:
        properties["Pace"] = {"rich_text": [{"text": {"content": pace}}]}

    icon = get_icon_for_record(activity_name)
    cover = get_cover_for_record(activity_name)

    try:
        client.pages.update(
            page_id=page_id,
            properties=properties,
            icon={"emoji": icon},
            cover={"type": "external", "external": {"url": cover}}
        )

    except Exception as e:
        print(f"Error updating record: {e}")


def write_new_record(client, database_id, activity_date, activity_type, activity_name, typeId, value, pace):
    properties = {
        "Date": {"date": {"start": activity_date}},
        "Activity Type": {"select": {"name": activity_type}},
        "Record": {"title": [{"text": {"content": activity_name}}]},
        "typeId": {"number": typeId},
        "PR": {"checkbox": True}
    }

    if value:
        properties["Value"] = {"rich_text": [{"text": {"content": value}}]}

    if pace:
        properties["Pace"] = {"rich_text": [{"text": {"content": pace}}]}

    icon = get_icon_for_record(activity_name)
    cover = get_cover_for_record(activity_name)

    try:
        client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            icon={"emoji": icon},
            cover={"type": "external", "external": {"url": cover}}
        )
    except Exception as e:
        print(f"Error writing new record: {e}")


def main():
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_PR_DB_ID")

    # garmin = Garmin(garmin_email, garmin_password)
    # garmin.login()
    #
    # client = Client(auth=notion_token)

    # records = garmin.get_personal_record()
    from _fake_personal_records import get_fake_prs
    records = get_fake_prs()
    filtered_records = [record for record in records if record.get('typeId') != 16]
    parsed_records = [PersonalRecord.model_validate(record) for record in filtered_records]

    for record in parsed_records:
        activity_date = record.start_time
        activity_type = record.activity_category

        typeId = record.get('typeId', 0)
        # activity_name = replace_activity_name_by_typeId(typeId)
        activity_name = record.personal_record.category
        # value, pace = format_garmin_value(record.get('value', 0), typeId)
        value = record.value
        pace = record.pace

        existing_pr_record = get_existing_record(client, database_id, activity_name)
        existing_date_record = get_record_by_date_and_name(client, database_id, activity_date, activity_name)

        if existing_date_record:
            update_record(client, existing_date_record['id'], activity_date, value, pace, activity_name, True)
            print(f"Updated existing record: {activity_type} - {activity_name}")
        elif existing_pr_record:
            existing_date = existing_pr_record['properties']['Date']['date']['start']
            if activity_date > existing_date:
                update_record(client, existing_pr_record['id'], existing_date, None, None, activity_name, False)
                print(f"Archived old record: {activity_type} - {activity_name}")

                write_new_record(client, database_id, activity_date, activity_type, activity_name, typeId, value,
                                 pace)
                print(f"Created new PR record: {activity_type} - {activity_name}")
            else:
                print(f"No update needed: {activity_type} - {activity_name}")
        else:
            write_new_record(client, database_id, activity_date, activity_type, activity_name, typeId, value, pace)
            print(f"Successfully written new record: {activity_type} - {activity_name}")

    assert 1


if __name__ == '__main__':
    main()
