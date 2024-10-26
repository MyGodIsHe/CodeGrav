import json
from collections import defaultdict
from typing import Iterator

import pygame
from pygame import Surface, Rect

from camera import camera
from render import Clickable, Drawable, draw_arrow


class Node(Clickable, Drawable):
    def __init__(self, id: int, x: int, y: int, text: str):
        self.id = id
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
        return pygame.Rect(camera.x + self.x - width / 2, camera.y + self.y - height / 2, width, height)


class Edge(Drawable):
    def __init__(self, id: int, start: Node, end: Node):
        self.id = id
        self.start = start
        self.end = end

    def draw(self, surface: Surface):
        draw_arrow(surface, self.start.rect(), self.end.rect(), 5, 10)


class Space:
    def __init__(self):
        self.nodes: dict[int, Node] = {}
        self.edges: list[Edge] = []
        self.last_id = 0

    @property
    def objects(self) -> Iterator[Drawable]:
        for e in self.edges:
            yield e
        for n in self.nodes.values():
            yield n

    def merge_nodes(self, node_ids: list[int], group: Node):
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
        edge = Edge(self.get_new_id(), start, end)
        self.edges.append(edge)
        self.edges_links[start.id].append(edge)
        if start.id != end.id:
            self.edges_links[end.id].append(edge)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def del_node(self, node: Node):
        del self.nodes[node.id]
        if node.id in self.edges_links:
            edges = self.edges_links.get(node.id)
            if edges:
                del self.edges_links[node.id]
                for edge in edges:
                    if edge in self.edges:
                        self.edges.remove(edge)

    def get_new_id(self) -> int:
        self.last_id += 1
        return self.last_id

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
        self.selected_rect = None
        with open(filename, 'r') as f:
            data = json.load(f)
        self.nodes = {
            n['id']: Node(**n)
            for n in data['nodes']
        }
        self.nodes = [
            Edge(e['id'], start=self.nodes[e['start']], end=self.nodes[e['start']])
            for e in data['edges']
        ]
        self.last_id = max(obj.id for obj in self.objects)
