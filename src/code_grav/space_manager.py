from code_grav.camera import camera
from code_grav.space import Space, SubSpace
from code_grav.utils import get_common_center


class SpaceManager:
    def __init__(self):
        self._spaces: list[Space | SubSpace] = [Space()]

    @property
    def space(self) -> Space:
        ss = self._spaces[-1]
        if isinstance(ss, SubSpace):
            return ss.space
        return ss

    def apply(self, sub_space: SubSpace):
        self._spaces.append(sub_space)
        x, y = get_common_center(sub_space.space.nodes.values())
        camera.x, camera.y = camera.window_to_world(x, y)

    def rollback(self) -> bool:
        if len(self._spaces) > 1:
            ss = self._spaces.pop()
            if isinstance(ss, SubSpace):
                camera.x = ss.x
                camera.y = ss.y
            return True
        return False
