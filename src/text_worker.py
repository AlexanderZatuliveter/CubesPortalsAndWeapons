from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import pygame

from text_common import create_text_texture, update_text_vbo


class TextWorker:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        rect_size: tuple[float, float],
        font: pygame.font.Font | None,
        font_file_path: str,
        shader: ShaderProgram | None,
        color: tuple[float, float, float]
    ) -> None:

        self.__rect: pygame.Rect = pygame.Rect(x, y, *rect_size)
        self.__color = color
        self.__text = text

        # Shader uniform locations
        self.__uColor = glGetUniformLocation(shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uTexture = glGetUniformLocation(shader, "uTexture")

        # Text rendering objects (created lazily)
        self._text_texture = 0
        self._text_size = (0, 0)
        self.__text_vao = None
        self.__text_vbo = None
        self.__font_file_path = font_file_path
        self.__font = font

    def draw(self) -> None:
        # Prepare text texture if needed
        if not self._text_texture or self._text_size == (0, 0) or getattr(self, "_last_text", None) != self.__text:

            self._text_texture, self._text_size, self.__text_vao, self.__text_vbo = create_text_texture(
                self.__text,
                self._text_texture,
                self.__text_vao,
                self.__text_vbo,
                self.__font,
                self.__font_file_path,
                int(self.__rect.height)
            )

            self._last_text = self.__text

        if not self._text_texture:
            return

        # compute centered position for the text inside the button rect
        text_width, text_height = self._text_size
        text_x = self.__rect.x + (self.__rect.width - text_width) / 2.0
        text_y = self.__rect.y + (self.__rect.height + text_height) / 2.0

        # update VBO for text quad
        update_text_vbo(text_x, text_y, self._text_texture, self._text_size, self.__text_vao, self.__text_vbo)

        # enable blending for text alpha
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # bind texture and draw the quad
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._text_texture)
        glUniform1i(self.__uTexture, 0)
        glUniform1i(self.__uUseTexture, 1)
        # keep color as white so text renders in original color, but you can tint
        glUniform3f(self.__uColor, *self.__color)

        glBindVertexArray(self.__text_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Ensure shader not left in textured mode for subsequent draws
        glUniform1i(self.__uUseTexture, 0)

    def update_text(self, text: str) -> None:
        self.__text = text
