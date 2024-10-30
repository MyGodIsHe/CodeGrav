import pygame

import app
import colors
from events import EventManager
from space_manager import SpaceManager


def main():
    window = app.Window().get()
    space_manager = SpaceManager()
    events = EventManager(space_manager)
    while True:
        pygame.transform.smoothscale(window.surface, window.surface.get_size())
        window.surface.fill(colors.space)
        for obj in space_manager.space.objects:
            obj.draw(window.surface)
        events.trigger_events()
        pygame.display.flip()


if __name__ == '__main__':
    main()
