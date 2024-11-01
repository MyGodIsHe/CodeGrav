from abc import ABC, abstractmethod

from pygame import Rect, Surface


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


class Node(Clickable, Drawable, ABC):
    id: int
    x: int
    y: int
    pins: list[BasePin]

    def get_pin_by_name(self, name: str) -> BasePin | None:
        for pin in self.pins:
            if pin.name == name:
                return pin
