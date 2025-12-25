

from OpenGL.GL import *  # type: ignore
import numpy as np


class OpenGLUtils:

    @staticmethod
    def create_square_vertices(size: float, x: float = 0.0, y: float = 0.0) -> np.ndarray:
        vertices = np.array([
            x, y,
            size, y,
            size, size,
            x, size,
        ], dtype=np.float32)
        return vertices

    @staticmethod
    def create_rectangle_vertices(width: float, height: float, x: float = 0.0, y: float = 0.0) -> np.ndarray:
        vertices = np.array([
            x, y,
            x + width, y,
            x + width, y + height,
            x, y + height,
        ], dtype=np.float32)
        return vertices

    @staticmethod
    def ortho(l, r, b, t, n, f):
        return np.array([
            [2 / (r - l), 0, 0, -(r + l) / (r - l)],
            [0, 2 / (b - t), 0, -(b + t) / (b - t)],
            [0, 0, -2 / (f - n), -(f + n) / (f - n)],
            [0, 0, 0, 1],
        ], dtype=np.float32)
