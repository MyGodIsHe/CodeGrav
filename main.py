from time import sleep

import pygame
import sys

import app
import colors
import exceptions
from events import EventsManager
from render import draw_dashed_rect
from space_manager import SpaceManager


def main():
    window = app.Window().get()
    space_manager = SpaceManager()
    events = EventsManager(space_manager)
    try:
        while True:
            pygame.transform.smoothscale(window.surface, window.surface.get_size())
            events.check()
            window.surface.fill(colors.white)
            for obj in space_manager.space.objects:
                obj.draw(window.surface)
            for obj in events.selected_objects:
                pygame.draw.rect(window.surface, (0, 0, 0), obj.rect(), 3)
            if events.selected_rect:
                draw_dashed_rect(window.surface, (0, 0, 0), events.selected_rect, 1, 10)
            pygame.display.flip()
    except exceptions.Exit:
        pass
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
