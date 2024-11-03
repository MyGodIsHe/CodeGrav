from abc import ABC, abstractmethod
from typing import Callable, Protocol, TypeAlias, Sequence

from pygame import Rect, Surface


class SpaceProtocol(Protocol):
    @abstractmethod
    def add_node(self, node: 'Node'):
        pass

    @abstractmethod
    def del_node(self, node: 'Node'):
        pass


ContextMenuItems: TypeAlias = list[tuple[str, Callable[[SpaceProtocol], None]]]


class Clickable(ABC):
    @abstractmethod
    def select_rect(self) -> Rect:
        pass


class Drawable(ABC):
    id: int
    x: int
    y: int

    @abstractmethod
    def draw(self, surface: Surface):
        pass


class BasePin(Drawable, Clickable, ABC):
    node: 'Node'
    name: str
    radius: int = 15


class Node(Clickable, Drawable, ABC):
    id: int
    x: int
    y: int
    pins: Sequence[BasePin]

    def get_pin_by_name(self, name: str) -> BasePin | None:
        for pin in self.pins:
            if pin.name == name:
                return pin

    @abstractmethod
    def get_context_menu_items(self) -> ContextMenuItems:
        pass
