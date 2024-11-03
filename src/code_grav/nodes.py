import pygame
from pygame import Surface, Rect

from code_grav import colors
from code_grav.camera import camera
from code_grav.sync_pins import SyncPins
from code_grav.pins import InvisiblePin, HalfPin, OutputPin, InputPin
from code_grav.render import draw_button, draw_circle, draw_text_top_button
from code_grav.space_types import Node, ContextMenuItems, SpaceProtocol, BasePin
from code_grav.utils import get_new_id, get_max_pin_id, generate_pos_pins


class Input(Node):
    half_width = 50
    width = half_width * 2

    def __init__(self, pin_events: SyncPins, x: int, y: int, pins: list[str], node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.pin_events = pin_events
        self.pin_events.add_handlers.append(self.add_pin_handler)
        self.pins = [
            OutputPin(self, pin, pin, self.half_width, 0)
            for pin in pins
        ]
        self.height = generate_pos_pins(self.pins, 100 - 15, 15)
        self.half_height = self.height // 2

    def draw(self, surface: Surface):
        draw_text_top_button(surface, self.select_rect(), 'Input', colors.space, colors.node_text, colors.node_border)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_width, self.y - self.half_height)
        return pygame.Rect(x, y, self.width, self.height)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("new pin", self.on_new_pin),
        ]

    def _new_pin(self, pin_name: str) -> BasePin | None:
        for pin in self.pins:
            if pin.name == pin_name:
                return
        pin = OutputPin(self, pin_name, pin_name, self.half_width, 0)
        self.pins.append(pin)
        self.height = generate_pos_pins(self.pins, self.height - 15, 15)
        self.half_height = self.height // 2
        return pin

    def on_new_pin(self, space: SpaceProtocol):
        max_int = get_max_pin_id(self.pins) + 1
        pin = self._new_pin(str(max_int))
        if pin:
            self.pin_events.add_pin(pin.name)

    def add_pin_handler(self, pin_name: str):
        self._new_pin(pin_name)


class Output(Node):
    half_width = 50
    width = half_width * 2

    def __init__(self, pin_events: SyncPins, x: int, y: int, pins: list[str], node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.pin_events = pin_events
        self.pin_events.add_handlers.append(self.add_pin_handler)
        self.pins = [
            InputPin(self, pin, pin, -self.half_width, 0)
            for pin in pins
        ]
        self.height = generate_pos_pins(self.pins, 100 - 15, 15)
        self.half_height = self.height // 2

    def draw(self, surface: Surface):
        draw_text_top_button(surface, self.select_rect(), 'Output', colors.space, colors.node_text, colors.node_border)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_width, self.y - self.half_height)
        return pygame.Rect(x, y, self.width, self.height)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("new pin", self.on_new_pin),
        ]

    def _new_pin(self, pin_name: str) -> BasePin | None:
        for pin in self.pins:
            if pin.name == pin_name:
                return
        pin = InputPin(self, pin_name, pin_name, -self.half_width, 0)
        self.pins.append(pin)
        self.height = generate_pos_pins(self.pins, self.height - 15, 15)
        self.half_height = self.height // 2
        return pin

    def on_new_pin(self, space: SpaceProtocol):
        max_int = get_max_pin_id(self.pins) + 1
        pin = self._new_pin(str(max_int))
        if pin:
            self.pin_events.add_pin(pin.name)

    def add_pin_handler(self, pin_name: str):
        self._new_pin(pin_name)


class Const(Node):
    half_size = 30
    size = half_size * 2

    def __init__(self, x: int, y: int, value: str = '1', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            InputPin(self, 'input', None, -self.half_size, 0),
            OutputPin(self, 'output', None, self.half_size, 0),
        ]

    def draw(self, surface: Surface):
        x, y = camera.world_to_window(self.x, self.y)
        draw_circle(surface, x, y, self.value, self.half_size)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_size, self.y - self.half_size)
        return pygame.Rect(x, y, self.size, self.size)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("delete node", lambda space: space.del_node(self)),
        ]


class If(Node):
    half_width = 70
    width = half_width * 2
    half_height = 60
    height = half_height * 2

    def __init__(self, x: int, y: int, value: str = 'IF', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            InputPin(self, 'first', None, -self.half_width, -25),
            InputPin(self, 'second', None, -self.half_width, 25),
            OutputPin(self, 'true', 'true', self.half_width, -25),
            OutputPin(self, 'false', 'false', self.half_width, 25),
        ]

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.value, colors.space, colors.node_text, colors.node_border)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_width, self.y - self.half_height)
        return pygame.Rect(x, y, self.width, self.height)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("delete node", lambda space: space.del_node(self)),
        ]


class Operator(Node):
    half_width = 70
    width = half_width * 2
    half_height = 50
    height = half_height * 2

    def __init__(self, x: int, y: int, value: str = '+', node_id: int | None = None):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            InputPin(self, 'first', None, -self.half_width, -25),
            InputPin(self, 'second', None, -self.half_width, 25),
            OutputPin(self, 'output', None, self.half_width, 0),
        ]

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.value, colors.space, colors.node_text, colors.node_border)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_width, self.y - self.half_height)
        return pygame.Rect(x, y, self.width, self.height)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("delete node", lambda space: space.del_node(self)),
        ]


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

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("delete node", lambda space: space.del_node(self)),
        ]


class SelfSpace(Node):
    half_width = 50
    width = half_width * 2
    half_height = 25
    height = half_height * 2

    def __init__(
            self,
            x: int,
            y: int,
            input_pins: list[str],
            output_pins: list[str],
            node_id: int | None = None,
    ):
        self.id = node_id or get_new_id()
        self.x = x
        self.y = y
        self.input_pins = []
        self.output_pins = []
        for pin in input_pins:
            self._new_input_pin(pin)
        for pin in output_pins:
            self._new_output_pin(pin)
        self.height = max(
            generate_pos_pins(self.input_pins, 100 - 15, 15),
            generate_pos_pins(self.output_pins, 100 - 15, 15),
        )
        self.half_height = self.height // 2

    @property
    def pins(self) -> list[BasePin]:
        return self.input_pins + self.output_pins

    def draw(self, surface: Surface):
        draw_text_top_button(surface, self.select_rect(), 'SelfSpace', colors.space, colors.node_text, colors.node_border)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        x, y = camera.world_to_window(self.x - self.half_width, self.y - self.half_height)
        return pygame.Rect(x, y, self.width, self.height)

    def add_node_handler(self, node: Node):
        if isinstance(node, Input):
            self.pins.append(HalfPin(self, f'input-{node.id}', 0, -25))
            self.generate_pos_pins('input')
        elif isinstance(node, Output):
            self.pins.append(HalfPin(self, f'output-{node.id}', 0, 25))
            self.generate_pos_pins('output')

    def generate_pos_pins(self, prefix: str):
        pins = [pin for pin in self.pins if pin.name.startswith(prefix)]
        generate_pos_pins(pins, self.height, 0)

    def get_context_menu_items(self) -> ContextMenuItems:
        return [
            ("new input pin", self.on_new_input_pin),
            ("new output pin", self.on_new_output_pin),
            ("delete node", lambda space: space.del_node(self)),
        ]

    def _new_input_pin(self, pin_name: str) -> BasePin | None:
        for pin in self.input_pins:
            if pin.name == pin_name:
                return
        pin = InputPin(self, pin_name, pin_name, -self.half_width, 0)
        self.input_pins.append(pin)
        self.height = generate_pos_pins(self.input_pins, self.height - 15, 15)
        self.half_height = self.height // 2
        return pin

    def on_new_input_pin(self, space: SpaceProtocol):
        max_int = get_max_pin_id(self.input_pins) + 1
        pin = self._new_input_pin(str(max_int))
        if pin:
            space.sync_input_pins.add_pin(pin.name)

    def add_input_pin_handler(self, pin_name: str):
        self._new_input_pin(pin_name)

    def _new_output_pin(self, pin_name: str) -> BasePin | None:
        for pin in self.output_pins:
            if pin.name == pin_name:
                return
        pin = OutputPin(self, pin_name, pin_name, self.half_width, 0)
        self.output_pins.append(pin)
        self.height = generate_pos_pins(self.output_pins, self.height - 15, 15)
        self.half_height = self.height // 2
        return pin

    def on_new_output_pin(self, space: SpaceProtocol):
        max_int = get_max_pin_id(self.output_pins) + 1
        pin = self._new_output_pin(str(max_int))
        if pin:
            space.sync_output_pins.add_pin(pin.name)

    def add_output_pin_handler(self, pin_name: str):
        self._new_output_pin(pin_name)
