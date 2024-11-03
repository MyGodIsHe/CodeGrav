import sys

import pygame

from code_grav import app, file_manager
from code_grav import colors
from code_grav.events import EventManager
from code_grav.space import Space
from code_grav.space_manager import SpaceManager


def main():
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
    else:
        filepath = None

    window = app.Window().get()
    if filepath:
        space_manager = file_manager.load_or_new(filepath)
    else:
        space_manager = SpaceManager(Space([('input1', '1')], [('output1', '1')]))
    events = EventManager(space_manager, filepath)
    while True:
        pygame.transform.smoothscale(window.surface, window.surface.get_size())
        window.surface.fill(colors.space)
        for obj in space_manager.space.objects:
            obj.draw(window.surface)
        events.trigger_events()
        pygame.display.flip()


if __name__ == '__main__':
    main()
