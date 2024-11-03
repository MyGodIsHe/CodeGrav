import pygame
from pygame import Surface, Rect

from code_grav import colors
from code_grav.camera import camera
from code_grav.render import draw_button, draw_circle
from code_grav.space_types import Node, BasePin


class Pin(BasePin):
    def __init__(self, node: Node, name: str, x: int, y: int, text: str):
        self.node: Node = node
        self.name = name
        self.x = x
        self.y = y
        self.text = text

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.text, colors.pin_bg, colors.pin_text)

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = self.node.x + self.x - half_size, self.node.y + self.y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class HalfPin(BasePin):
    def __init__(self, node: Node, name: str, x: int, y: int):
        self.node: Node = node
        self.name = name
        self.x = x
        self.y = y

    def draw(self, surface: Surface):
        x, y = self.node.x + self.x, self.node.y + self.y
        x, y = camera.world_to_window(x, y)
        draw_circle(surface, x, y, radius=self.radius)

    def select_rect(self) -> Rect:
        size = self.radius * 2
        x, y = self.node.x + self.x - self.radius, self.node.y + self.y - self.radius
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class InvisiblePin(Pin):
    def __init__(self, node: Node, name: str, x: int, y: int):
        super().__init__(node, name, x, y, '')

    def draw(self, surface: Surface):
        pass

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = self.node.x + self.x - half_size, self.node.y + self.y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class NamedInputPin(BasePin):
    def __init__(self, node: Node, name: str, text: str | None, x: int, y: int):
        self.node: Node = node
        self.name = name
        self.x = x
        self.y = y
        self.text = text

    def draw(self, surface: Surface):
        x, y = self.node.x + self.x, self.node.y + self.y
        x, y = camera.world_to_window(x, y)
        draw_circle(surface, x, y, radius=self.radius)
        if self.text:
            font = pygame.font.Font(None, 18)
            text_surface = font.render(self.text, True, colors.white)
            text_x = x + 10 + self.radius
            text_y = y - text_surface.get_height() // 2
            surface.blit(text_surface, (text_x, text_y))

    def select_rect(self) -> Rect:
        half_size = self.radius
        size = half_size * 2
        x, y = self.node.x + self.x - half_size, self.node.y + self.y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class NamedOutputPin(BasePin):
    def __init__(self, node: Node, name: str, text: str | None, x: int, y: int):
        self.node: Node = node
        self.name = name
        self.x = x
        self.y = y
        self.text = text

    def draw(self, surface: Surface):
        x, y = self.node.x + self.x, self.node.y + self.y
        x, y = camera.world_to_window(x, y)
        draw_circle(surface, x, y, radius=self.radius)
        if self.text:
            font = pygame.font.Font(None, 18)
            text_surface = font.render(self.text, True, colors.white)
            text_x = x - text_surface.get_width() - 10 - self.radius
            text_y = y - text_surface.get_height() // 2
            surface.blit(text_surface, (text_x, text_y))

    def select_rect(self) -> Rect:
        half_size = self.radius
        size = half_size * 2
        x, y = self.node.x + self.x - half_size, self.node.y + self.y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)
