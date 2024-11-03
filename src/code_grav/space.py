from typing import Iterator

import pygame
from pygame import Surface

from code_grav.nodes import SubSpace, Input, Output
from code_grav.sync_pins import SyncPins
from code_grav.render import draw_arrow
from code_grav.space_types import Drawable, Node, Clickable, BasePin, BaseEdge
from code_grav.utils import get_new_id, get_pin_by_name


class Edge(BaseEdge):
    def __init__(self, start: BasePin, end: BasePin, edge_id: int | None = None):
        self.id = edge_id or get_new_id()
        self.start: BasePin = start
        self.end: BasePin = end

    def draw(self, surface: Surface):
        draw_arrow(surface, self.start.select_rect(), self.end.select_rect(), 5, 10)


class Space:
    def __init__(self, input_pins: list[tuple[str, str]], output_pins: list[tuple[str, str]]):
        self.nodes: dict[int, Node] = {}
        self.edges: list[Edge] = []
        self.sync_input_pins = SyncPins()
        self.input_node = Input(self.sync_input_pins, -200, 0, input_pins)
        self.add_node(self.input_node)
        self.sync_output_pins = SyncPins()
        self.output_node = Output(self.sync_output_pins, 200, 0, output_pins)
        self.add_node(self.output_node)

    @property
    def objects(self) -> Iterator[Drawable]:
        for n in self.nodes.values():
            yield n
        for e in self.edges:
            yield e

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

    def new_subspace_from_nodes(self, x, y, node_ids: list[int]) -> SubSpace:
        input_pins: list[tuple[str, str]] = []
        output_pins: list[tuple[str, str]] = []
        for edge in self.edges:
            if edge.start.node.id not in node_ids or edge.end.node.id not in node_ids:
                if edge.start.node.id in node_ids:
                    i = str(len(output_pins) + 1)
                    output_pins.append(('output' + i, i))
                if edge.end.node.id in node_ids:
                    i = str(len(input_pins) + 1)
                    input_pins.append(('input' + i, i))

        new_space = Space(input_pins, output_pins)
        ss = SubSpace(x, y, new_space, input_pins, output_pins)

        new_edges = []
        start_i = 1
        end_i = 1
        for edge in self.edges:
            if edge.start.node.id in node_ids and edge.end.node.id in node_ids:
                new_space.edges.append(edge)
            else:
                if edge.start.node.id in node_ids:
                    i = 'output' + str(start_i)
                    pin = get_pin_by_name(ss.space.output_node.pins, i)
                    ss.space.edges.append(Edge(edge.start, pin))
                    edge.start = get_pin_by_name(ss.output_pins, i)
                    start_i += 1
                if edge.end.node.id in node_ids:
                    i = 'input' + str(end_i)
                    pin = get_pin_by_name(ss.space.input_node.pins, i)
                    ss.space.edges.append(Edge(pin, edge.end))
                    edge.end = get_pin_by_name(ss.input_pins, i)
                    end_i += 1
                new_edges.append(edge)

        self.edges = new_edges

        for node_id in node_ids:
            if node_id in self.nodes:
                new_space.nodes[node_id] = self.nodes.pop(node_id)

        self.add_node(ss)

        ss.space.sync_input_pins.add_handlers.append(ss.add_input_pin_handler)
        ss.space.sync_output_pins.add_handlers.append(ss.add_output_pin_handler)
        return ss

    def add_connect(self, start: BasePin, end: BasePin):
        edge = Edge(start, end)
        self.edges.append(edge)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def del_node(self, node: Node):
        del self.nodes[node.id]
        need_del_edges = set()
        for pin in node.pins:
            for edge in self.edges:
                if pin in [edge.start, edge.end]:
                    need_del_edges.add(edge)
        for edge in need_del_edges:
            self.edges.remove(edge)
