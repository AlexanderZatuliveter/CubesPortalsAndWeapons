

import math
from game.systems.float_rect import FloatRect


class RotatedRect:
    def __init__(self, rect: FloatRect) -> None:
        self.rect = rect

    def __rotate_point(
        self,
        point: tuple[float, float],
        center: tuple[float, float],
        angle: float
    ) -> tuple[float, float]:
        """Поворот точки вокруг центра (угол в радианах)"""

        x, y = point
        cx, cy = center

        s = math.sin(angle)
        c = math.cos(angle)

        x -= cx
        y -= cy

        x_new = x * c - y * s
        y_new = x * s + y * c

        return (x_new + cx, y_new + cy)

    def get_points(self, angle: float) -> list[tuple[float, float]]:
        """Return rectangle corners rotated around its center.

        Points are returned relative to the rectangle origin (0,0) so
        the vertex shader can add `uPlayerPos` to place the object in world
        coordinates without double-offsetting.
        """
        w, h = self.rect.width, self.rect.height
        center = (w / 2.0, h / 2.0)

        corners = [
            (0.0, 0.0),
            (w, 0.0),
            (w, h),
            (0.0, h),
        ]

        return [self.__rotate_point(p, center, angle) for p in corners]
