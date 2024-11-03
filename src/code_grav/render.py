import pygame

from code_grav import colors


def draw_button(surface, rect, text, rect_color, text_color, border_color=None, border_radius=3):
    pygame.draw.rect(surface, rect_color, rect)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_radius)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_text_top_button(surface, rect, text, rect_color, text_color, border_color=None, border_radius=3):
    pygame.draw.rect(surface, rect_color, rect)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_radius)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_x = rect.center[0] - text_surface.get_width() // 2
    text_y = rect.top + 10
    surface.blit(text_surface, (text_x, text_y))


def draw_flexible_button(surface, center, text, rect_color, text_color, border_color=None, border_radius=3, padding=10):
    x, y = center
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_width, text_height = text_surface.get_size()
    rect_width, rect_height = text_width + 2 * padding, text_height + 2 * padding
    button_rect = pygame.Rect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
    text_rect = text_surface.get_rect(center=button_rect.center)
    pygame.draw.rect(surface, rect_color, button_rect)
    if border_color:
        pygame.draw.rect(surface, border_color, button_rect, border_radius)
    surface.blit(text_surface, text_rect)


def draw_circle(
        surface,
        x: int,
        y: int,
        text: str | None = None,
        radius: int = 25,
        bg_color=colors.space,
        text_color=colors.white,
):
    pygame.draw.circle(surface, bg_color, (x, y), radius)
    pygame.draw.circle(surface, text_color, (x, y), radius, 3)
    if text:
        font = pygame.font.Font(None, 24)
        text = font.render(text, True, text_color)
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)


def draw_arrow(screen, rect1, rect2, thickness, circle_radius, color=colors.edge):
    pygame.draw.circle(screen, color, rect1.center, thickness)
    pygame.draw.line(screen, color, rect1.center, rect2.center, thickness)
    pygame.draw.circle(screen, color, rect2.center, circle_radius)


def draw_link(screen, from_rect, to_point, thickness, color=colors.edge):
    pygame.draw.circle(screen, color, from_rect.center, thickness)
    pygame.draw.line(screen, color, from_rect.center, to_point, thickness)
    pygame.draw.circle(screen, color, to_point, thickness)


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
