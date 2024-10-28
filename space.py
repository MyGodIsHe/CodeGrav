import json
from abc import ABC
from typing import Iterator

import pygame
from pygame import Surface, Rect

from camera import camera
from render import Clickable, Drawable, draw_arrow, draw_button, draw_circle

_LAST_ID = 0


class Pin(Drawable):
    def __init__(self, node: 'Node', name: str, x: int, y: int, text: str):
        self.node: Node = node
        self.name = name
        self.relative_x = x
        self.relative_y = y
        self.text = text

    def draw(self, surface: Surface):
        draw_button(surface, self.rect(), self.text)

    def rect(self) -> Rect:
        width = 50
        height = 50
        x, y = self.node.x + self.relative_x, self.node.y + self.relative_y
        return pygame.Rect(*camera.world_to_window(x, y), width, height)


class InvisiblePin(Pin):
    def __init__(self, node: 'Node', name: str, x: int, y: int):
        super().__init__(node, name, x, y, '')

    def draw(self, surface: Surface):
        pass

    def rect(self) -> Rect:
        width = 50
        height = 50
        x, y = self.node.x + self.relative_x, self.node.y + self.relative_y
        return pygame.Rect(*camera.world_to_window(x, y), width, height)


class Node(Clickable, Drawable, ABC):
    id: int
    x: int
    y: int
    pins: list[Pin]


class Const(Node):
    def __init__(self, x: int, y: int, value: str = '1', id: int | None = None):
        self.id = id or get_new_id()
        self.x = x
        self.y = y
        self.value = value
        self.pins = [
            InvisiblePin(self, 'value', -25, -25),
        ]

    def draw(self, surface: Surface):
        x, y = camera.world_to_window(self.x, self.y)
        draw_circle(surface, x, y, self.value)

    def select_rect(self) -> Rect:
        width = 50
        height = 50
        x, y = camera.world_to_window(self.x - width / 2, self.y - height / 2)
        return pygame.Rect(x, y, width, height)


class If(Node):
    def __init__(self, x: int, y: int, id: int | None = None):
        self.id = id or get_new_id()
        self.x = x
        self.y = y
        self.text = 'IF'
        self.pins = [
            Pin(self, 'input1', -50, -75, 'o'),
            Pin(self, 'input2', 0, -75, 'o'),
            Pin(self, 'false', -50, 25, 'f'),
            Pin(self, 'true', 0, 25, 't'),
        ]

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.text)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        width = 100
        height = 50
        x, y = camera.world_to_window(self.x - width / 2, self.y - height / 2)
        return pygame.Rect(x, y, width, height)


class SubSpace(Node):
    def __init__(self, x: int, y: int):
        self.id = id or get_new_id()
        self.x = x
        self.y = y
        self.text = 'SubSpace'
        self.pins = []
        self.space: Space | None = None

    def draw(self, surface: Surface):
        draw_button(surface, self.select_rect(), self.text)
        for pin in self.pins:
            pin.draw(surface)

    def select_rect(self) -> Rect:
        width = 100
        height = 50
        x, y = camera.world_to_window(self.x - width / 2, self.y - height / 2)
        return pygame.Rect(x, y, width, height)


class Edge(Drawable):
    def __init__(self, start: Pin, end: Pin, id: int | None = None):
        self.id = id or get_new_id()
        self.start: Pin = start
        self.end: Pin = end

    def draw(self, surface: Surface):
        draw_arrow(surface, self.start.rect(), self.end.rect(), 5, 10)


class Space:
    def __init__(self):
        self.nodes: dict[int, Node] = {}
        self.edges: list[Edge] = []

    @property
    def objects(self) -> Iterator[Drawable]:
        for e in self.edges:
            yield e
        for n in self.nodes.values():
            yield n

    def was_select_rect(self, event) -> Clickable | None:
        for obj in self.objects:
            if isinstance(obj, Clickable) and obj.select_rect().collidepoint(event.pos):
                return obj

    def was_select_linked_rect(self, event) -> tuple[Pin, pygame.Rect] | None:
        for obj in self.objects:
            if isinstance(obj, Node):
                for pin in obj.pins:
                    rect = pin.rect()
                    if rect.collidepoint(event.pos):
                        return pin, rect

    def merge_nodes(self, node_ids: list[int], ss: SubSpace) -> 'Space':
        detached_space = Space()

        # Update edges to point to the new node and collect edges of removed nodes
        new_edges = []
        for edge in self.edges:
            if edge.start.node.id in node_ids and edge.end.node.id in node_ids:
                # Add to detached space if both nodes are in the list
                detached_space.edges.append(edge)
            else:
                # Update start or end if necessary to point to the new_node
                if edge.start.node.id in node_ids:
                    i = len(ss.pins) + 1
                    pin = Pin(ss, 'start', -25, i * 50 - 25, f'o {i}')
                    ss.pins.append(pin)
                    edge.start = pin
                if edge.end.node.id in node_ids:
                    i = len(ss.pins) + 1
                    pin = Pin(ss, 'end', -25, i * 50 - 25, f'o {i}')
                    ss.pins.append(pin)
                    edge.end = pin
                new_edges.append(edge)

        self.edges = new_edges

        # Add detached nodes and their edges to the detached space
        for node_id in node_ids:
            if node_id in self.nodes:
                detached_space.nodes[node_id] = self.nodes.pop(node_id)

        return detached_space

    def add_connect(self, start: Pin, end: Pin):
        edge = Edge(start, end)
        self.edges.append(edge)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def save(self, filename: str):
        data = {
            'nodes': [
                {'id': n.id, 'x': n.x, 'y': n.y, 'text': n.text}
                for n in self.nodes.values()
            ],
            'edges': [
                {'start': e.start.id, 'end': e.end.id}
                for e in self.edges
            ],
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load(self, filename: str):
        global _LAST_ID
        with open(filename, 'r') as f:
            data = json.load(f)
        self.nodes = {
            n['id']: Node(**n)
            for n in data['nodes']
        }
        self.nodes = [
            Edge(id=e['id'], start=self.nodes[e['start']], end=self.nodes[e['start']])
            for e in data['edges']
        ]
        _LAST_ID = max(obj.id for obj in self.objects)


def get_new_id() -> int:
    global _LAST_ID
    _LAST_ID += 1
    return _LAST_ID
