from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import ctypes

import pygame

from consts import BLUE, BUTTON_HEIGHT, BUTTON_WIDTH, GREY, GREY_2, ORANGE


class Button:
    def __init__(self, x: float, y: float, text: str, shader: ShaderProgram, function) -> None:
        self.__rect: pygame.Rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.__text = text
        self.__color = GREY
        self.__active = False
        self.__function = function

        # Shader uniform locations
        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uTexture = glGetUniformLocation(shader, "uTexture")

        # Background quad (uses positions in screen/game units)
        vertices = np.array([
            0.0, 0.0,
            BUTTON_WIDTH, 0.0,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            0.0, BUTTON_HEIGHT,
        ], dtype=np.float32)

        self.__vertex_count = 4

        # VAO/VBO for background rectangle
        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        # Dynamic offset buffer (we'll update it per-draw)
        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # keeps backwards compatibility with instanced usage

        glBindVertexArray(0)

        # Text rendering objects (created lazily)
        self._text_texture = 0
        self._text_size = (0, 0)
        self.__text_vao = None
        self.__text_vbo = None

    def update(self, mouse_pos: tuple[int, int], mouse_pressed: tuple[bool, bool, bool]) -> None:
        if self.__rect.collidepoint(mouse_pos):
            if mouse_pressed[0]:  # ЛКМ зажата
                self.__color = BLUE
                self.__active = True
            else:
                if not self.__active:
                    self.__color = ORANGE
        else:
            if not self.__active:
                self.__color = GREY_2

        # После клика возвращаем active = False, чтобы кнопка дальше реагировала
        if not mouse_pressed[0] and self.__active:
            self.__active = False
            self.__perform_function()

    def _create_text_texture(self, font: pygame.font.Font | None = None) -> None:
        """Render text to a pygame surface and upload as an OpenGL texture."""
        if font is None:
            # choose a size relative to button height
            font_size = max(8, int(self.__rect.height * 0.6))
            font = pygame.font.Font(None, font_size)

        # render text to surface with alpha
        text_surf = font.render(self.__text, True, (255, 255, 255))
        text_surf = text_surf.convert_alpha()
        w, h = text_surf.get_size()

        # get pixel data (flipped vertically for GL)
        pixel_data = pygame.image.tostring(text_surf, "RGBA", True)

        # create or replace texture
        if self._text_texture:
            glDeleteTextures([self._text_texture])

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixel_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        self._text_texture = tex
        self._text_size = (w, h)

        # create text VAO/VBO (positions are absolute in screen/game units)
        if not self.__text_vao:
            self.__text_vao = glGenVertexArrays(1)
            self.__text_vbo = glGenBuffers(1)

    def _update_text_vbo(self, x: float, y: float) -> None:
        """Upload vertex+texcoord data for the text quad positioned at (x,y)."""
        if not self._text_texture:
            return

        w, h = self._text_size

        # vertices: x,y,u,v  (triangle fan)
        verts = np.array([
            x, y, 0.0, 0.0,
            x + w, y, 1.0, 0.0,
            x + w, y - h, 1.0, 1.0,
            x, y - h, 0.0, 1.0,
        ], dtype=np.float32)

        glBindVertexArray(self.__text_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.__text_vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)

        stride = 4 * 4  # 4 floats per vertex, 4 bytes each
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))

        glBindVertexArray(0)

    def draw(self, font: pygame.font.Font | None = None) -> None:
        glBindVertexArray(self.__vao)

        # update offset for background
        offset = np.array([float(self.__rect.x), float(self.__rect.y)], dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, offset.nbytes, offset)

        glUniform1i(self.__uIsPlayer, 0)
        glUniform1i(self.__uUseTexture, 0)
        # send RGBA with alpha=1.0
        glUniform3f(self.__uColor, *self.__color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)

        # Prepare text texture if needed
        if not self._text_texture or self._text_size == (0, 0) or getattr(self, "_last_text", None) != self.__text:
            self._create_text_texture(font)
            self._last_text = self.__text

        if not self._text_texture:
            return

        # compute centered position for the text inside the button rect
        text_width, text_height = self._text_size
        text_x = self.__rect.x + (self.__rect.width - text_width) / 2.0
        text_y = self.__rect.y + (self.__rect.height + text_height) / 2.0

        # update VBO for text quad
        self._update_text_vbo(text_x, text_y)

        # enable blending for text alpha
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # bind texture and draw the quad
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._text_texture)
        glUniform1i(self.__uTexture, 0)
        glUniform1i(self.__uUseTexture, 1)
        # keep color as white so text renders in original color, but you can tint
        glUniform3f(self.__uColor, 1.0, 1.0, 1.0)

        glBindVertexArray(self.__text_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Ensure shader not left in textured mode for subsequent draws
        glUniform1i(self.__uUseTexture, 0)

    def __perform_function(self) -> None:
        if self.__function is None:
            return
        self.__function()
