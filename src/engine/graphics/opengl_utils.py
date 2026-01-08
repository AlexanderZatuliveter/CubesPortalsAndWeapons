

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
    def create_vertices_with_points(points: list[tuple[float, float]]) -> np.ndarray:
        vertices = np.array([
            points[0][0], points[0][1],
            points[1][0], points[1][1],
            points[2][0], points[2][1],
            points[3][0], points[3][1],
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

    @staticmethod
    def look_at(eye, target, up):

        def normalize(v):
            norm = np.linalg.norm(v)
            if norm == 0:
                return v
            return v / norm

        f = normalize(target - eye)
        s = normalize(np.cross(f, up))
        u = np.cross(s, f)

        return np.array([
            [s[0], u[0], -f[0], -np.dot(s, eye)],
            [s[1], u[1], -f[1], -np.dot(u, eye)],
            [s[2], u[2], -f[2], np.dot(f, eye)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
