from abc import ABC, abstractmethod

import pygame
from pygame import Surface, Rect

import colors


class Clickable(ABC):
    @abstractmethod
    def select_rect(self) -> Rect:
        pass


class Drawable(ABC):
    id: int
    x: int
    y: int

    @abstractmethod
    def draw(self, surface: Surface):
        pass


def draw_button(surface, rect, text, rect_color=colors.blue, text_color=colors.white):
    pygame.draw.rect(surface, rect_color, rect)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_circle(
        surface,
        x: int,
        y: int,
        text: str | None = None,
        radius: int = 25,
        bg_color=colors.blue,
        text_color=colors.white,
):
    pygame.draw.circle(surface, bg_color, (x, y), radius)
    if text:
        font = pygame.font.Font(None, 24)
        text = font.render(text, True, text_color)
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)


def draw_arrow(screen, rect1, rect2, thickness, circle_radius, color=(0, 0, 0)):
    start_x, start_y = rect1.center
    end = intersection_with_rectangle(rect2, rect1.center)
    if not end:
        return
    end_x, end_y = end

    # Рисуем линию
    pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), thickness)

    # Рисуем кружок на конце линии
    pygame.draw.circle(screen, color, (int(end_x), int(end_y)), circle_radius)


def draw_link(screen, from_rect, to_point, thickness, color=(0, 0, 0)):
    end_x, end_y = to_point
    start = intersection_with_rectangle(from_rect, to_point)
    if not start:
        return
    start_x, start_y = start

    # Рисуем линию
    pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), thickness)


def intersection_with_rectangle(rect, line_direction):
    center_x, center_y = rect.center
    width, height = rect.width, rect.height
    x, y = line_direction

    # Половина ширины и высоты прямоугольника
    half_width = width / 2
    half_height = height / 2

    # Координаты границ прямоугольника
    left = center_x - half_width
    right = center_x + half_width
    bottom = center_y - half_height
    top = center_y + half_height

    # Вектор направления для прямой
    vx = x - center_x
    vy = y - center_y

    # Если вектор направления имеет нулевую длину, вернуть центр как пересечение
    if vx == 0 and vy == 0:
        return center_x, center_y

    # Время пересечения с вертикальными границами прямоугольника
    tx1 = (left - center_x) / vx if vx != 0 else None
    tx2 = (right - center_x) / vx if vx != 0 else None

    # Время пересечения с горизонтальными границами прямоугольника
    ty1 = (bottom - center_y) / vy if vy != 0 else None
    ty2 = (top - center_y) / vy if vy != 0 else None

    # Все времена пересечения
    t_values = [t for t in [tx1, tx2, ty1, ty2] if t is not None]

    # Находим минимальное положительное время пересечения
    tmin = min([t for t in t_values if t >= 0], default=None)

    if tmin is None:
        return None

    # Вычисление координат точки пересечения
    intersection_x = center_x + tmin * vx
    intersection_y = center_y + tmin * vy

    return intersection_x, intersection_y


def draw_dashed_rect(surface, color, rect, width=1, dash_length=5):
    x1, y1, x2, y2 = rect.left, rect.top, rect.right, rect.bottom
    points = [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]
    for p1, p2 in points:
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = (dx**2 + dy**2)**0.5
        steps = max(1, int(length / dash_length))
        for step in range(0, steps, 2):
            start = step / steps
            end = (step + 1) / steps
            start_pos = (p1[0] + int(dx * start), p1[1] + int(dy * start))
            end_pos = (p1[0] + int(dx * end), p1[1] + int(dy * end))
            pygame.draw.line(surface, color, start_pos, end_pos, width)
