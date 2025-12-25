from OpenGL.GL import *  # type: ignore

import numpy as np
import pygame
import ctypes


def create_text_texture(
    text: str,
    text_texture,
    text_vao,
    text_vbo,
    font: pygame.font.Font | None,
    font_file_path: str,
    font_height: int
):
    """Render text to a pygame surface and upload as an OpenGL texture.
    Return text_texture, text_size, text_vao, text_vbo."""
    if font is None:
        # choose a size relative to button height
        font_size = max(8, font_height)
        font = pygame.font.Font(font_file_path, font_size)

    # render text to surface with alpha
    text_surf = font.render(text, True, (255, 255, 255))
    text_surf = text_surf.convert_alpha()
    w, h = text_surf.get_size()

    # get pixel data (flipped vertically for GL)
    pixel_data = pygame.image.tostring(text_surf, "RGBA", True)

    # create or replace texture
    if text_texture:
        glDeleteTextures([text_texture])

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixel_data)
    glBindTexture(GL_TEXTURE_2D, 0)

    text_texture = tex
    text_size = (w, h)

    # create text VAO/VBO (positions are absolute in screen/game units)
    if not text_vao:
        text_vao = glGenVertexArrays(1)
        text_vbo = glGenBuffers(1)

    return text_texture, text_size, text_vao, text_vbo


def update_text_vbo(
    x: float,
    y: float,
    text_texture,
    text_size: tuple[int, int],
    text_vao,
    text_vbo
) -> None:
    """Upload vertex+texcoord data for the text quad positioned at (x,y)."""
    if not text_texture:
        return

    w, h = text_size

    # vertices: x,y,u,v  (triangle fan)
    verts = np.array([
        x, y, 0.0, 0.0,
        x + w, y, 1.0, 0.0,
        x + w, y - h, 1.0, 1.0,
        x, y - h, 0.0, 1.0,
    ], dtype=np.float32)

    glBindVertexArray(text_vao)
    glBindBuffer(GL_ARRAY_BUFFER, text_vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)

    stride = 4 * 4  # 4 floats per vertex, 4 bytes each
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))

    glBindVertexArray(0)
