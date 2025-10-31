

from OpenGL.GL import *  # type: ignore
import pygame


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
