import pygame


class Window:
    _window = None

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CodeGrav")
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)

    @classmethod
    def get(cls) -> 'Window':
        if not cls._window:
            cls._window = Window()
        return cls._window
