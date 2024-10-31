import json
from typing import Iterator

import pygame
from pygame import Surface

from code_grav.nodes import SubSpace
from code_grav.pins import Pin
from code_grav.render import draw_arrow
from code_grav.space_types import Drawable, Node, Clickable, BasePin
from code_grav.utils import get_new_id


class Edge(Drawable):
    def __init__(self, start: BasePin, end: BasePin, id: int | None = None):
        self.id = id or get_new_id()
        self.start: BasePin = start
        self.end: BasePin = end

    def draw(self, surface: Surface):
        draw_arrow(surface, self.start.select_rect(), self.end.select_rect(), 5, 10)


class Space:
    def __init__(self):
        self.nodes: dict[int, Node] = {}
        self.edges: list[Edge] = []
        self.add_handlers: list = []
        self.del_handlers: list = []

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

    def was_select_linked_rect(self, event) -> tuple[BasePin, pygame.Rect] | None:
        for obj in self.objects:
            if isinstance(obj, Node):
                for pin in obj.pins:
                    rect = pin.select_rect()
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

    def add_connect(self, start: BasePin, end: BasePin):
        edge = Edge(start, end)
        self.edges.append(edge)

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        for handler in self.add_handlers:
            handler(node)

    def del_node(self, node: Node):
        del self.nodes[node.id]
        need_del_edges = set()
        for pin in node.pins:
            for edge in self.edges:
                if pin in [edge.start, edge.end]:
                    need_del_edges.add(edge)
        for edge in need_del_edges:
            self.edges.remove(edge)
        for handler in self.del_handlers:
            handler(node)

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
