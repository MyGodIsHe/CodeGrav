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
        self.relative_x = x
        self.relative_y = y
        self.text = text

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.text, colors.pin_bg, colors.pin_text)

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = self.node.x + self.relative_x - half_size, self.node.y + self.relative_y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class HalfPin(BasePin):
    def __init__(self, node: Node, name: str, x: int, y: int):
        self.node: Node = node
        self.name = name
        self.relative_x = x
        self.relative_y = y

    def draw(self, surface: Surface):
        x, y = self.node.x + self.relative_x, self.node.y + self.relative_y
        x, y = camera.world_to_window(x, y)
        draw_circle(surface, x, y, radius=15)

    def select_rect(self) -> Rect:
        half_size = 15
        size = half_size * 2
        x, y = self.node.x + self.relative_x - half_size, self.node.y + self.relative_y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class HalfTextPin(BasePin):
    def __init__(self, node: Node, name: str, x: int, y: int, text: str, text_x: int, text_y: int):
        self.node: Node = node
        self.name = name
        self.relative_x = x
        self.relative_y = y
        self.text = text
        self.text_x = text_x
        self.text_y = text_y

    def draw(self, surface: Surface):
        x, y = self.node.x + self.relative_x, self.node.y + self.relative_y
        x, y = camera.world_to_window(x, y)
        draw_circle(surface, x, y, radius=15)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, colors.white)
        text_rect = text_surface.get_rect(center=(x + self.text_x, y + self.text_y))
        surface.blit(text_surface, text_rect)

    def select_rect(self) -> Rect:
        half_size = 15
        size = half_size * 2
        x, y = self.node.x + self.relative_x - half_size, self.node.y + self.relative_y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)


class InvisiblePin(Pin):
    def __init__(self, node: Node, name: str, x: int, y: int):
        super().__init__(node, name, x, y, '')

    def draw(self, surface: Surface):
        pass

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = self.node.x + self.relative_x - half_size, self.node.y + self.relative_y - half_size
        return pygame.Rect(*camera.world_to_window(x, y), size, size)
