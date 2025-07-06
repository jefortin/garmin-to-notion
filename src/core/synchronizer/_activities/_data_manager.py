from datetime import datetime
from typing import Iterable

from garminconnect import Garmin as GarminClient

from src.core.garmin import DataManager
from ._models import GarminActivity
from ...garmin._data_manager import T


class ActivityDataManager(DataManager[GarminActivity]):
    """
    Manages the data for activities, including loading and saving activity data.
    """

    def _list_entries(self, garmin_client: GarminClient, start_date: datetime, end_date: datetime) -> Iterable[T]:

