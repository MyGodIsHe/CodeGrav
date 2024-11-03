from typing import Sequence

from code_grav.nodes import Node
from code_grav.space_types import BasePin

_LAST_ID = 0


def normalize_rect(rect):
    if rect.width < 0:
        rect.x += rect.width
        rect.width = abs(rect.width)
    if rect.height < 0:
        rect.y += rect.height
        rect.height = abs(rect.height)
    return rect


def get_common_center(nodes: list[Node]):
    assert nodes
    total_x, total_y = 0, 0

    for node in nodes:
        center = node.select_rect().center
        total_x += center[0]
        total_y += center[1]

    common_center_x = total_x // len(nodes)
    common_center_y = total_y // len(nodes)

    return common_center_x, common_center_y


def get_new_id() -> int:
    global _LAST_ID
    _LAST_ID += 1
    return _LAST_ID


def set_last_id(value: int):
    global _LAST_ID
    _LAST_ID = value


def get_max_pin_id(pins: list[BasePin], prefix: str = '') -> int:
    max_int = 0
    prefix_len = len(prefix)
    for pin in pins:
        if pin.name.startswith(prefix):
            name_part = pin.name[prefix_len:]
            if name_part.isdigit():
                pin_id = int(name_part)
                if pin_id > max_int:
                    max_int = pin_id
    return max_int


def generate_pos_pins(pins: Sequence[BasePin], height: int, top_offset: int) -> int:
    total = len(pins)
    height = max(height, sum(pin.radius * 2 for pin in pins) + (total - 1) * 10)
    step = height / (total + 1)
    offset = - step * (total - 1) / 2
    for i, pin in enumerate(pins):
        pin.y = top_offset + offset + i * step
    return top_offset + height


def get_pin_by_name(pins: Sequence[BasePin], name: str) -> BasePin | None:
    for pin in pins:
        if pin.name == name:
            return pin
