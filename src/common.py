

from OpenGL.GL import *  # type: ignore
import numpy
import pygame


def ortho(l, r, b, t, n, f):
    """Orthographic projection matrix"""
    return numpy.array([
        [2 / (r - l), 0, 0, 0],
        [0, 2 / (t - b), 0, 0],
        [0, 0, -2 / (f - n), 0],
        [-(r + l) / (r - l), -(t + b) / (t - b), -(f + n) / (f - n), 1]
    ], dtype=numpy.float32).T

# def ortho(tx, ty, tz):
#     return numpy.array([
#         [1, 0, 0, tx],
#         [0, 1, 0, ty],
#         [0, 0, 1, tz],
#         [0, 0, 0, 1]
#     ], dtype=numpy.float32)


def translate(tx, ty, tz):
    M = numpy.identity(4, dtype=numpy.float32)
    M[3][0], M[3][1], M[3][2] = tx, ty, tz
    return M


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
