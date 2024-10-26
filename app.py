import pygame


class Window:
    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        self.width = infoObject.current_w
        self.height = infoObject.current_h
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
