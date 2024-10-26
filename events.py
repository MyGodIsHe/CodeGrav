from enum import StrEnum

import pygame

import exceptions
from camera import camera
from render import Clickable
from space import Space, Node, Edge

start_drag_pos = None
_EVENTS = []


def event_rule(condition):
    def decorator(func):
        _EVENTS.append((condition, func))
        return func
    return decorator


class DragType(StrEnum):
    scene = 'scene'
    object = 'object'
    rect = 'rect'


class EventsManager:
    def __init__(self, space: Space):
        self.start_drag_pos = None
        self.drag_type: DragType | None = None
        self.space: Space = space
        self.selected_objects: list[Clickable] = []
        self.selected_rect = None

    def check(self):
        for event in pygame.event.get():
            for condition, handler in _EVENTS:
                if condition(event):
                    handler(self, event)

    def was_select(self, event):
        for obj in self.space.objects:
            if isinstance(obj, Clickable) and obj.rect().collidepoint(event.pos):
                return obj

    @event_rule(lambda e: e.type == pygame.QUIT)
    @event_rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)
    def event_exit(self, event):
        raise exceptions.Exit()

    @event_rule(lambda e: (
            e.type == pygame.MOUSEBUTTONUP
            and e.button == 1
            and pygame.key.get_mods() == pygame.KMOD_NONE
    ))
    def event_select_node(self, event):
        if self.selected_rect and max(self.selected_rect.width, self.selected_rect.height) > 1:
            return
        obj = self.was_select(event)
        if obj:
            self.selected_objects = [obj]

    @event_rule(lambda e: (
            e.type == pygame.MOUSEBUTTONDOWN
            and e.button == 1
            and pygame.key.get_mods() == pygame.KMOD_NONE
    ))
    def event_multi_select(self, event):
        if self.drag_type:
            return
        if self.selected_objects == [self.was_select(event)]:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.object
            self.selected_rect = None
            return
        self.start_drag_pos = event.pos
        self.drag_type = DragType.rect

    @event_rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_n)
    def event_create_node(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        node = Node(self.space.get_new_id(), mouse_x - camera.x, mouse_y - camera.y, "X")
        self.space.nodes[node.id] = node

    @event_rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and e.button == 3)
    def event_drag(self, event):
        if not self.drag_type:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.scene

    @event_rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button in [1, 3])
    def event_drop(self, event):
        self.start_drag_pos = None
        self.drag_type = None
        self.selected_rect = None

    @event_rule(lambda e: e.type == pygame.MOUSEMOTION)
    def event_move(self, event):
        if self.drag_type == DragType.scene:
            dx, dy = event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]
            self.start_drag_pos = event.pos
            camera.x += dx
            camera.y += dy
        elif self.drag_type == DragType.object:
            dx, dy = event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]
            self.start_drag_pos = event.pos
            self.selected_objects[0].x += dx
            self.selected_objects[0].y += dy
        elif self.drag_type == DragType.rect:
            self.selected_rect = pygame.Rect(
                self.start_drag_pos,
                (event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]),
            )

    @event_rule(lambda e: (
            e.type == pygame.MOUSEBUTTONDOWN
            and e.button == 1
            and pygame.key.get_mods() & pygame.KMOD_SHIFT
    ))
    def event_create_connect(self, event):
        if len(self.selected_objects) == 1:
            target = self.was_select(event)
            if target and self.selected_objects[0] != target:
                self.space.edges.append(Edge(self.selected_objects[0], target))
