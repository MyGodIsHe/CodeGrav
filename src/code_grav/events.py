import sys
from enum import StrEnum

import pygame

from code_grav import colors
from code_grav.app import Window
from code_grav.camera import camera
from code_grav.nodes import SubSpace, Const, Operator, If, SelfSpace, Input, Output
from code_grav.render import draw_dashed_rect, draw_button, draw_link, draw_flexible_button
from code_grav.space_manager import SpaceManager
from code_grav.space_types import Node, BasePin
from code_grav.utils import normalize_rect, get_common_center


DOUBLE_CLICK_THRESHOLD = 500
_CLICK_TIME = 0


class DragType(StrEnum):
    scene = 'scene'
    object = 'object'
    rect = 'rect'
    link = 'link'


class EventStorage:
    def __init__(self):
        self._events = []

    def rule(self, condition):
        def decorator(func):
            self._events.append((condition, func))
            return func
        return decorator

    def trigger_events(self, event_self):
        for event in pygame.event.get():
            for condition, func in self._events:
                if condition(event):
                    func(event_self, event)


class EventManager:
    def __init__(self, space_manager: SpaceManager):
        self.space_manager = space_manager
        self._main = MainEvents(self, space_manager)
        self._current = self._main

    def trigger_events(self):
        self._current.trigger_events()

    def switch_to_main(self):
        self._current = self._main

    def switch_to_context_menu(self, mouse_x: int, mouse_y: int):
        self._current = ContextMenuEvents(self, self.space_manager, mouse_x, mouse_y)

    def switch_to_input(self, callback):
        w = Window.get()
        self._current = InputEvents(self, self.space_manager, w.half_width, w.half_height, callback)


class MainEvents:
    event = EventStorage()

    def __init__(self, event_manager: EventManager, space_manager: SpaceManager):
        self.event_manager = event_manager
        self.space_manager: SpaceManager = space_manager
        self.window = Window.get()
        self.start_drag_pos = None
        self.drag_was_move = False
        self.drag_type: DragType | None = None
        self.selected_objects: list[Node] = []
        self.selected_rect = None
        self.link_drag_start: pygame.Rect | None = None
        self.link_drag_pin: BasePin | None = None

    def trigger_events(self):
        self.event.trigger_events(self)
        for obj in self.selected_objects:
            pygame.draw.rect(self.window.surface, colors.white, obj.select_rect(), 4)
        if self.selected_rect:
            draw_dashed_rect(self.window.surface, colors.white, self.selected_rect, 1, 10)
        if self.link_drag_start:
            draw_link(self.window.surface, self.link_drag_start, pygame.mouse.get_pos(), 5)

    @event.rule(lambda e: e.type == pygame.QUIT)
    def event_game_exit(self, event):
        sys.exit()

    @event.rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)
    def event_escape(self, event):
        if self.space_manager.rollback():
            self.selected_objects = []
        else:
            pygame.quit()
            sys.exit()

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button == 1)
    def event_select_node_or_link_point(self, event):
        if self.selected_rect and max(self.selected_rect.width, self.selected_rect.height) > 5:
            return
        obj = self.space_manager.space.was_select_rect(event)
        if obj:
            self.selected_objects = [obj]

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and e.button == 1)
    def event_multi_select(self, event):
        if self.drag_type:
            return
        if self.space_manager.space.was_select_rect(event) in self.selected_objects:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.object
            self.selected_rect = None
            return
        result = self.space_manager.space.was_select_linked_rect(event)
        if result:
            pin, rect = result
            self.link_drag_start = rect
            self.link_drag_pin = pin
            self.drag_type = DragType.link
        else:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.rect

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and e.button == 3)
    def event_drag(self, event):
        if not self.drag_type:
            self.start_drag_pos = event.pos
            self.drag_type = DragType.scene

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button == 1)
    def event_drop_left(self, event):
        if self.drag_type == DragType.rect and self.selected_rect:
            self.selected_objects = []
            for obj in self.space_manager.space.nodes.values():
                if self.selected_rect.colliderect(obj.select_rect()):
                    self.selected_objects.append(obj)
        elif self.drag_type == DragType.link:
            result = self.space_manager.space.was_select_linked_rect(event)
            if result:
                pin, _ = result
                self.space_manager.space.add_connect(self.link_drag_pin, pin)
        self.start_drag_pos = None
        self.drag_type = None
        self.selected_rect = None
        self.link_drag_start = None
        self.link_drag_pin = None

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button == 3)
    def event_drop_right(self, event):
        if not self.drag_was_move:
            was_select = self.space_manager.space.was_select_rect(event)
            if not was_select:
                self.event_manager.switch_to_context_menu(*event.pos)
        self.start_drag_pos = None
        self.drag_was_move = False
        self.drag_type = None
        self.selected_rect = None

    @event.rule(lambda e: e.type == pygame.MOUSEMOTION)
    def event_move(self, event):
        if self.drag_type == DragType.scene:
            dx, dy = event.pos[0] - self.start_drag_pos[0], event.pos[1] - self.start_drag_pos[1]
            self.start_drag_pos = event.pos
            camera.x -= dx
            camera.y -= dy
            self.drag_was_move = True
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

    @event.rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_g)
    def event_create_subspace(self, event):
        if not self.selected_objects:
            return
        x, y = get_common_center(self.selected_objects)
        x, y = camera.window_to_world(x, y)
        ss = SubSpace(x, y)
        self.space_manager.space.add_node(ss)
        ss.space = self.space_manager.space.merge_nodes([obj.id for obj in self.selected_objects], ss)
        self.selected_objects = [ss]

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONDOWN and is_double_click())
    def event_enter_to_subspace(self, event):
        obj = self.space_manager.space.was_select_rect(event)
        if obj and isinstance(obj, SubSpace):
            self.space_manager.apply(obj)
            self.selected_objects = []


class ContextMenuEvents:
    event = EventStorage()

    def __init__(self, event_manager: EventManager, space_manager: SpaceManager, mouse_x: int, mouse_y: int):
        self.window = Window.get()
        self.event_manager: EventManager = event_manager
        self.space_manager: SpaceManager = space_manager
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        width = 90
        height = 30
        self.menu_rects = {
            (mouse_x, mouse_y + height * i, width, height): cls
            for i, cls in enumerate([
                Const,
                Operator,
                If,
                SelfSpace,
                Input,
                Output,
            ])
        }

    def trigger_events(self):
        self.event.trigger_events(self)
        for rect_params, cls in self.menu_rects.items():
            draw_button(
                self.window.surface,
                pygame.Rect(*rect_params),
                cls.__name__,
                colors.menu_bg,
                colors.menu_text,
            )

    @event.rule(lambda e: e.type == pygame.QUIT)
    def event_game_exit(self, event):
        sys.exit()

    @event.rule(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)
    def event_escape(self, event):
        pygame.quit()
        sys.exit()

    @event.rule(lambda e: e.type == pygame.MOUSEBUTTONUP and e.button == 1)
    def event_select_node(self, event):
        selected_cls = None
        for rect_params, cls in self.menu_rects.items():
            if pygame.Rect(*rect_params).collidepoint(event.pos):
                selected_cls = cls
                break
        if selected_cls:
            x, y = camera.window_to_world(self.mouse_x, self.mouse_y)
            if selected_cls in [Const, Operator, If]:
                self.event_manager.switch_to_input(
                    lambda text: self.space_manager.space.add_node(selected_cls(x, y, text))
                )
                return
            else:
                self.space_manager.space.add_node(selected_cls(x, y))
        self.event_manager.switch_to_main()


class InputEvents:
    event = EventStorage()

    def __init__(self, event_manager: EventManager, space_manager: SpaceManager, x: int, y: int, callback):
        self.window = Window.get()
        self.event_manager: EventManager = event_manager
        self.space_manager: SpaceManager = space_manager
        self.x = x
        self.y = y
        self.callback = callback
        self.text = ''

    def trigger_events(self):
        self.event.trigger_events(self)
        draw_flexible_button(
            self.window.surface,
            (self.x, self.y),
            self.text,
            colors.menu_bg,
            colors.menu_text,
        )

    @event.rule(lambda e: e.type == pygame.KEYDOWN)
    def event_texting(self, event):
        if event.key == pygame.K_RETURN:
            self.callback(self.text)
            self.event_manager.switch_to_main()
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.event_manager.switch_to_main()
        else:
            self.text += event.unicode


def is_double_click():
    global _CLICK_TIME
    current_time = pygame.time.get_ticks()
    is_double = current_time - _CLICK_TIME < DOUBLE_CLICK_THRESHOLD
    _CLICK_TIME = current_time
    return is_double
