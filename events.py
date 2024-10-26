import sys
from enum import StrEnum

import pygame

from camera import camera
from render import Clickable
from space import Node, SubSpace
from space_manager import SpaceManager
from utils import normalize_rect, get_common_center


DOUBLE_CLICK_THRESHOLD = 500
_EVENTS = []
_CLICK_TIME = 0


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
    def __init__(self, space_manager: SpaceManager):
        self.start_drag_pos = None
        self.drag_type: DragType | None = None
        self.space_manager: SpaceManager = space_manager
        self.selected_objects: list[Node] = []
        self.selected_rect = None

    def check(self):
        for event in pygame.event.get():
            for condition, handler in _EVENTS:
                if condition(event):
                    handler(self, event)

    def was_select(self, event) -> Node | None:
        for obj in self.space_manager.space.objects:
            if isinstance(obj, Clickable) and obj.rect().collidepoint(event.pos):
                return obj

    @event_rule(lambda e: e.type == pygame.QUIT)
    def event_game_exit(self, event):
        sys.exit()

    @event_rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)
    def event_escape(self, event):
        if self.space_manager.rollback():
            self.selected_objects = []
        else:
            pygame.quit()
            sys.exit()

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
        if self.was_select(event) in self.selected_objects:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.object
            self.selected_rect = None
            return
        self.start_drag_pos = event.pos
        self.drag_type = DragType.rect

    @event_rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_n)
    def event_create_node(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y = camera.window_to_world(mouse_x, mouse_y)
        self.space_manager.space.add_node(Node(x, y, "X"))

    @event_rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and e.button == 3)
    def event_drag(self, event):
        if not self.drag_type:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.scene

    @event_rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button in [1, 3])
    def event_drop(self, event):
        if self.drag_type == DragType.rect and self.selected_rect:
            self.selected_objects = []
            for obj in self.space_manager.space.nodes.values():
                if self.selected_rect.colliderect(obj) and self.selected_rect.contains(obj):
                    self.selected_objects.append(obj)
        self.start_drag_pos = None
        self.drag_type = None
        self.selected_rect = None

    @event_rule(lambda e: e.type == pygame.MOUSEMOTION)
    def event_move(self, event):
        if self.drag_type == DragType.scene:
            dx, dy = event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]
            self.start_drag_pos = event.pos
            camera.x -= dx
            camera.y -= dy
        elif self.drag_type == DragType.object:
            dx, dy = event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]
            self.start_drag_pos = event.pos
            for obj in self.selected_objects:
                obj.x += dx
                obj.y += dy
        elif self.drag_type == DragType.rect:
            self.selected_rect = normalize_rect(pygame.Rect(
                self.start_drag_pos,
                (event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]),
            ))

    @event_rule(lambda e: (
            e.type == pygame.MOUSEBUTTONDOWN
            and e.button == 1
            and pygame.key.get_mods() & pygame.KMOD_SHIFT
    ))
    def event_create_connect(self, event):
        if len(self.selected_objects) == 1:
            target = self.was_select(event)
            if target and self.selected_objects[0] != target:
                self.space_manager.space.add_connect(self.selected_objects[0], target)

    @event_rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_g)
    def event_create_subspace(self, event):
        if not self.selected_objects:
            return
        x, y = get_common_center(self.selected_objects)
        x, y = camera.window_to_world(x, y)
        ss = SubSpace(x, y)
        self.space_manager.space.add_node(ss)
        ss.space = self.space_manager.space.merge_nodes([obj.id for obj in self.selected_objects], ss)
        self.selected_objects = [ss]

    @event_rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and is_double_click())
    def event_enter_to_subspace(self, event):
        obj = self.was_select(event)
        if obj and isinstance(obj, SubSpace):
            self.space_manager.apply(obj)
            self.selected_objects = []


def is_double_click():
    global _CLICK_TIME
    current_time = pygame.time.get_ticks()
    is_double = current_time - _CLICK_TIME < DOUBLE_CLICK_THRESHOLD
    _CLICK_TIME = current_time
    return is_double
