

from OpenGL.GL import *  # type: ignore
import pygame

from consts import ORANGE, RED, YELLOW
from direction_enum import DirectionEnum
from physics import Physics


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
    # end GL_QUADS draw
    glEnd()
    glColor3f(*color)

    # start GL_LINE_LOOP draw
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)

    # end GL_LINE_LOOP draw
    glEnd()

    # GL_QUADS draw again
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


# def load_texture(path: str):
#     surface = pygame.image.load(path)
#     image = pygame.image.tostring(surface, "RGBA", True)
#     width, height = surface.get_rect().size

#     texid = glGenTextures(1)
#     glBindTexture(GL_TEXTURE_2D, texid)
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#     glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
#     return texid, width, height


# def draw_texture(texid: wrapper.Wrapper, x: float, y: float, width: float, height: float) -> None:
#     glEnable(GL_TEXTURE_2D)
#     glBindTexture(GL_TEXTURE_2D, texid)
#     glTexCoord2f(0, 0)
#     glVertex2f(x, y)
#     glTexCoord2f(1, 0)
#     glVertex2f(x + width, y)
#     glTexCoord2f(1, 1)
#     glVertex2f(x + width, y + height)
#     glTexCoord2f(0, 1)
#     glVertex2f(x, y + height)
#     glDisable(GL_TEXTURE_2D)


def load_texture(path: str):
    surface = pygame.image.load(path).convert_alpha()

    image = pygame.image.tostring(surface, "RGBA")
    width, height = surface.get_rect().size

    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

    return texid, width, height


def draw_texture(texid: int, x: float, y: float, width: float, height: float) -> None:
    glEnd()

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texid)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)

    glTexCoord2f(1, 0)
    glVertex2f(x + width, y)

    glTexCoord2f(1, 1)
    glVertex2f(x + width, y + height)

    glTexCoord2f(0, 1)
    glVertex2f(x, y + height)
    glEnd()

    glDisable(GL_TEXTURE_2D)

    glBegin(GL_QUADS)
