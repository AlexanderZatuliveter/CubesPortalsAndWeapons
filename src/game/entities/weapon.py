

import ctypes
import numpy as np
from OpenGL.GL import *  # type: ignore

from engine.common import load_texture
from engine.graphics.renderer import Renderer
from game.consts import BLOCK_SIZE


class Weapon:
    def __init__(self, image_shader, image_path: str, flip_x: bool = False, flip_y: bool = True) -> None:
        self.__shader = image_shader
        self.__renderer = Renderer()

        self.__texture, ratio = load_texture(image_path)

        w = BLOCK_SIZE * ratio[0]
        h = BLOCK_SIZE * ratio[1]
        x = 0
        y = 0

        u0, u1 = (1.0, 0.0) if flip_x else (0.0, 1.0)
        v0, v1 = (1.0, 0.0) if flip_y else (0.0, 1.0)

        vertices = np.array([
            x, y, u0, v0,
            x + w, y, u1, v0,
            x + w, y + h, u1, v1,
            x, y + h, u0, v1,
        ], dtype=np.float32)

        self.__vao, self.__vbo = self.__renderer.create_vao_vbo(vertices)

        stride = 4 * 4  # 4 row by 4 row (vertices)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))

        glBindVertexArray(0)

        # Cache uniform locations for faster access
        glUseProgram(self.__shader)
        self.__uPlayerPos = glGetUniformLocation(self.__shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(self.__shader, "uIsPlayer")
        self.__uUseTexture = glGetUniformLocation(self.__shader, "uUseTexture")
        self.__uTexture = glGetUniformLocation(self.__shader, "uTexture")
        self.__uColor = glGetUniformLocation(self.__shader, "uColor")
        glUseProgram(0)

    def draw(self, position=(100, 100)):
        self.__renderer.draw_texture(
            position, self.__vao, self.__shader,
            self.__uPlayerPos, self.__uIsPlayer,
            self.__uUseTexture, self.__uTexture,
            self.__texture, self.__uColor
        )
