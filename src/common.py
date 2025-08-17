

from OpenGL.GL import *  # type: ignore
import pygame

from consts import ORANGE, RED
from direction_enum import DirectionEnum
from physics import Physics
from renderer import Renderer


def debug_draw_square(x: float, y: float, size: float, physics: Physics, renderer: Renderer):

    size = 4.0

    renderer.add_quad(x - 2.0, y - 2.0, size, (0 / 255, 255 / 255, 0 / 255))

    point1, point2 = physics.collidepoints(DirectionEnum.RIGHT)
    renderer.add_quad(point1[0] - 2.0, point1[1] - 2.0, size, ORANGE)
    renderer.add_quad(point2[0] - 2.0, point2[1] - 2.0, size, ORANGE)

    point1, point2 = physics.collidepoints(DirectionEnum.LEFT)
    renderer.add_quad(point1[0] - 2.0, point1[1] - 2.0, size, ORANGE)
    renderer.add_quad(point2[0] - 2.0, point2[1] - 2.0, size, ORANGE)

    point1, point2 = physics.collidepoints(DirectionEnum.UP)
    renderer.add_quad(point1[0] - 2.0, point1[1] - 2.0, size, RED)
    renderer.add_quad(point2[0] - 2.0, point2[1] - 2.0, size, RED)

    point1, point2 = physics.collidepoints(DirectionEnum.DOWN)
    renderer.add_quad(point1[0] - 2.0, point1[1] - 2.0, size, RED)
    renderer.add_quad(point2[0] - 2.0, point2[1] - 2.0, size, RED)


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
