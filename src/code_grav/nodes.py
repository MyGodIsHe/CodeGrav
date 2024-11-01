import pygame
from pygame import Surface, Rect

from code_grav import colors
from code_grav.camera import camera
from code_grav.pins import InvisiblePin, HalfPin, HalfTextPin
from code_grav.render import draw_button, draw_circle
from code_grav.space_types import Node
from code_grav.utils import get_new_id


class Input(Node):
    def __init__(self, x: int, y: int, node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.pins = [
            InvisiblePin(self, 'input', 0, 0),
        ]

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), 'I', colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = camera.world_to_window(self.x - half_size, self.y - half_size)
        return pygame.Rect(x, y, size, size)


class Output(Node):
    def __init__(self, x: int, y: int, node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.pins = [
            InvisiblePin(self, 'output', 0, 0),
        ]

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), 'O', colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = camera.world_to_window(self.x - half_size, self.y - half_size)
        return pygame.Rect(x, y, size, size)


class Const(Node):
    def __init__(self, x: int, y: int, value: str = '1', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            InvisiblePin(self, 'value', 0, 0),
        ]

    def draw(self, surface: Surface):
        x, y = camera.world_to_window(self.x, self.y)
        draw_circle(surface, x, y, self.value)

    def select_rect(self) -> Rect:
        half_size = 25
        size = half_size * 2
        x, y = camera.world_to_window(self.x - half_size, self.y - half_size)
        return pygame.Rect(x, y, size, size)


class If(Node):
    def __init__(self, x: int, y: int, value: str = 'IF', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            HalfPin(self, 'input1', -25, -25),
            HalfPin(self, 'input2', 25, -25),
            HalfTextPin(self, 'false', -25, 25, 'f', 0, 7),
            HalfTextPin(self, 'true', 25, 25, 't', 0, 7),
        ]

    def draw(self, surface: Surface):
        for pin in self.pins:
            pin.draw(surface)
        draw_button(surface, self.select_rect(), self.value, colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        h_width = 50
        h_height = 25
        x, y = camera.world_to_window(self.x - h_width, self.y - h_height)
        return pygame.Rect(x, y, h_width * 2, h_height * 2)


class Operator(Node):
    def __init__(self, x: int, y: int, value: str = '+', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            HalfPin(self, 'input1', -25, -25),
            HalfPin(self, 'input2', 25, -25),
            HalfPin(self, 'output', 0, 25),
        ]

    def draw(self, surface: Surface):
        for pin in self.pins:
            pin.draw(surface)
        draw_button(surface, self.select_rect(), self.value, colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        h_width = 50
        h_height = 25
        x, y = camera.world_to_window(self.x - h_width, self.y - h_height)
        return pygame.Rect(x, y, h_width * 2, h_height * 2)


class SubSpace(Node):
    def __init__(self, x: int, y: int, node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.text = 'SubSpace'
        self.pins = []
        self.space: 'Space' | None = None

    def draw(self, surface: Surface):
        for pin in self.pins:
            pin.draw(surface)
        draw_button(surface, self.select_rect(), self.text, colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        h_width = 50
        h_height = 25
        x, y = camera.world_to_window(self.x - h_width, self.y - h_height)
        return pygame.Rect(x, y, h_width * 2, h_height * 2)


class SelfSpace(Node):
    h_width = 50
    h_height = 25
    width = h_width * 2
    height = h_height * 2

    def __init__(self, x: int, y: int, space: 'Space', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.text = 'SelfSpace'
        self.pins = []
        space.add_handlers.append(self.add_node_handler)
        space.del_handlers.append(self.del_node_handler)
        for node in space.nodes.values():
            self.add_node_handler(node)

    def draw(self, surface: Surface):
        for pin in self.pins:
            pin.draw(surface)
        draw_button(surface, self.select_rect(), self.text, colors.space, colors.node_text, colors.node_border)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.h_width, self.y - self.h_height)
        return pygame.Rect(x, y, self.width, self.height)

    def add_node_handler(self, node: Node):
        if isinstance(node, Input):
            self.pins.append(HalfPin(self, f'input-{node.id}', 0, -25))
            self.generate_pos_pins('input')
        elif isinstance(node, Output):
            self.pins.append(HalfPin(self, f'output-{node.id}', 0, 25))
            self.generate_pos_pins('output')

    def del_node_handler(self, node: Node):
        if isinstance(node, Input):
            self.remove_pin(f'input-{node.id}')
            self.generate_pos_pins('input')
        elif isinstance(node, Output):
            self.remove_pin(f'output-{node.id}')
            self.generate_pos_pins('output')

    def generate_pos_pins(self, prefix: str):
        pins = [pin for pin in self.pins if pin.name.startswith(prefix)]
        total = len(pins)
        step = self.width / (total + 1)
        offset = - step * (total - 1) / 2
        for i, pin in enumerate(pins):
            pin.x = offset + i * step

    def remove_pin(self, name: str):
        need_del_pin = None
        for pin in self.pins:
            if pin.name == name:
                need_del_pin = pin
                break
        if need_del_pin:
            self.pins.remove(need_del_pin)
