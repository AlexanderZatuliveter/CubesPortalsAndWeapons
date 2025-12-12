from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import ctypes

import pygame

from common import get_resource_path
from consts import SCORES_HEIGHT, SCORES_WIDTH
from text_worker import TextWorker


class Scores:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        shader: ShaderProgram | None,
        color: tuple[float, float, float]
    ) -> None:

        self.__rect: pygame.Rect = pygame.Rect(x, y, SCORES_WIDTH, SCORES_HEIGHT)
        self.__color = color
        self.__text = text

        # Dynamic offset buffer (we'll update it per-draw)
        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # keeps backwards compatibility with instanced usage

        glBindVertexArray(0)

        self.__text_worker = TextWorker(
            x=self.__rect.x,
            y=self.__rect.y + SCORES_HEIGHT,
            text=self.__text,
            rect_size=(self.__rect.width, self.__rect.height),
            font=None,
            font_file_path=get_resource_path("_content/fonts/WDXLLubrifontSC-Regular.ttf"),
            shader=shader,
            color=self.__color
        )

    def draw(self) -> None:
        self.__text_worker.draw()

    def update_text(self, text: str) -> None:
        self.__text = text
        self.__text_worker.update_text(text)
