import json
from typing import Iterator

import pygame
from pygame import Surface, Rect

from camera import camera
from render import Clickable, Drawable, draw_arrow


_LAST_ID = 0


class Node(Clickable, Drawable):
    def __init__(self, x: int, y: int, text: str, id: int | None = None):
        self.id = id or get_new_id()
        self.x = x
        self.y = y
        self.text = text

    def draw(self, surface: Surface):
        rect_color = (0, 128, 255)
        text_color = (255, 255, 255)
        rect = self.rect()
        pygame.draw.rect(surface, rect_color, rect)

        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, text_color)

        text_rect = text_surface.get_rect(center=rect.center)

        surface.blit(text_surface, text_rect)

    def rect(self) -> Rect:
        width = 100
        height = 50
        x, y = camera.world_to_window(self.x - width / 2, self.y - height / 2)
        return pygame.Rect(x, y, width, height)


class SubSpace(Node):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "SubSpace")
        self.space: Space | None = None


class Edge(Drawable):
    def __init__(self, start: Node, end: Node, id: int | None = None):
        self.id = id or get_new_id()
        self.start = start
        self.end = end

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

    def merge_nodes(self, node_ids: list[int], group: Node) -> 'Space':
        detached_space = Space()

        # Update edges to point to the new node and collect edges of removed nodes
        new_edges = []
        for edge in self.edges:
            if edge.start.id in node_ids and edge.end.id in node_ids:
                # Add to detached space if both nodes are in the list
                detached_space.edges.append(edge)
            else:
                # Update start or end if necessary to point to the new_node
                if edge.start.id in node_ids:
                    edge.start = group
                if edge.end.id in node_ids:
                    edge.end = group
                new_edges.append(edge)

        self.edges = new_edges

        # Add detached nodes and their edges to the detached space
        for node_id in node_ids:
            if node_id in self.nodes:
                detached_space.nodes[node_id] = self.nodes.pop(node_id)

        return detached_space

    def add_connect(self, start: Node, end: Node):
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
