from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

from garminconnect import Garmin as GarminClient
from pydantic import BaseModel


class GarminModel(BaseModel):
    """
    Base class for all pydantic models representing Garmin entities.
    """
    ...


T = TypeVar('T', bound='GarminModel')


class DataManager(ABC, Generic[T]):
    """
    Class responsible for interacting with the Garmin API for a specific model.
    """

    def __init__(self, garmin_client: GarminClient):
        self.__garmin_client = garmin_client

    def list_entries(self, page_number: int = 1, items_per_page: int = 10) -> Iterable[T]:
        """
        Lists entries from Garmin within the specified date range.
        """
        return self._list_entries(self.__garmin_client, page_number, items_per_page)

    @abstractmethod
    def _list_entries(self, garmin_client: GarminClient, page_number: int, items_per_page: int) -> Iterable[T]:
        """
        Lists entries within the specified date range using the Garmin client.
        """
        ...
