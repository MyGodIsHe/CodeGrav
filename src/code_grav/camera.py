from code_grav.app import Window


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        window = Window().get()
        self.half_w = window.width / 2
        self.half_h = window.height / 2

    def window_to_world(self, mouse_x: int, mouse_y: int) -> tuple[float, float]:
        x = mouse_x - self.half_w
        y = mouse_y - self.half_h
        return self.x + x, self.y + y

    def world_to_window(self, world_x: float, world_y: float) -> tuple[int, int]:
        x = world_x - self.x + self.half_w
        y = world_y - self.y + self.half_h
        return int(x), int(y)


camera = Camera()
