from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ._models import NotionModel

T = TypeVar("T")


class NotionProperty(NotionModel, ABC, Generic[T]):
    value: T

    @abstractmethod
    def get_insert_template(self) -> dict:
        """
        Returns the template to insert the property value into a Notion database.
        """
        pass

    @abstractmethod
    def get_filter_template(self) -> dict:
        """
        Returns the template to filter for the property's value in a Notion database.
        """
        pass

    def equals(self, other: NotionProperty) -> bool:
        """
        Returns True if the two properties are equal.
        """
        if type(self) != type(other):
            return False

        return self.value == other.value


class CheckboxProperty(NotionProperty[bool]):
    def get_insert_template(self) -> dict:
        return {"checkbox": self.value}

    def get_filter_template(self) -> dict:
        return {"checkbox": {"equals": self.value}}
