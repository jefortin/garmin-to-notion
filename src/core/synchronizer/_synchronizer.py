from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

T = TypeVar('T')


class DataSynchronizer(ABC, Generic[T]):
    """
    Logical entity that handles the synchronization of data to Notion.
    """

    def synchronize(self):
        """
        Synchronizes data between Garmin and Notion.
        """
        raise NotImplementedError("TODO")

    @abstractmethod
    def _fetch_data(self) -> Iterable[T]:
        """
        Fetches the data to synchronize to Notion.
        """
        ...
