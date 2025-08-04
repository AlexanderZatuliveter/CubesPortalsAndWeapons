

from OpenGL.GL import *  # type: ignore

from consts import ORANGE, RED, YELLOW
from direction_enum import DirectionEnum
from physics import Physics  # type: ignore


def draw_square_center(x: float, y: float, color: tuple[float, float, float], size: float = 4.0) -> None:
    half = size / 2
    glColor3f(*color)
    glVertex2f(x - half, y - half)
    glVertex2f(x + half, y - half)
    glVertex2f(x + half, y + half)
    glVertex2f(x - half, y + half)


def draw_square_topleft(x: float, y: float, color: tuple[float, float, float], size: float) -> None:
    glColor3f(*color)
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)


def draw_square_topleft_outline(x: float, y: float, color: tuple[float, float, float], size: float) -> None:
    glEnd()
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)
    glEnd()
    glBegin(GL_QUADS)


def debug_draw_square(x: float, y: float, size: float, physics: Physics):

    draw_square_topleft_outline(x - 1, y - 1, YELLOW, size + 2)
    draw_square_center(x, y, (0 / 255, 255 / 255, 0 / 255))

    point1, point2 = physics.collidepoints(DirectionEnum.RIGHT)
    draw_square_center(*point1, ORANGE)
    draw_square_center(*point2, ORANGE)

    point1, point2 = physics.collidepoints(DirectionEnum.LEFT)
    draw_square_center(*point1, ORANGE)
    draw_square_center(*point2, ORANGE)

    point1, point2 = physics.collidepoints(DirectionEnum.UP)
    draw_square_center(*point1, RED)
    draw_square_center(*point2, RED)

    point1, point2 = physics.collidepoints(DirectionEnum.DOWN)
    draw_square_center(*point1, RED)
    draw_square_center(*point2, RED)
