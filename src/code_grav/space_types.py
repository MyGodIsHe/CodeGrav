from abc import ABC, abstractmethod
from typing import Callable, Protocol, TypeAlias, Sequence

from pygame import Rect, Surface

from code_grav.sync_pins import SyncPins


class SpaceProtocol(Protocol):
    sync_input_pins: SyncPins
    sync_output_pins: SyncPins
    input_node: 'Node'
    output_node: 'Node'
    nodes: dict[str, 'Node']
    edges: list['BaseEdge']

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


class BaseNamedPin(BasePin, ABC):
    title: str


class Node(Clickable, Drawable, ABC):
    id: int
    x: int
    y: int

    @abstractmethod
    def get_context_menu_items(self) -> ContextMenuItems:
        pass

    @property
    @abstractmethod
    def pins(self) -> Sequence[BasePin]:
        pass


class BaseEdge(Drawable, ABC):
    start: BasePin
    end: BasePin

    @abstractmethod
    def draw(self, surface: Surface):
        pass
