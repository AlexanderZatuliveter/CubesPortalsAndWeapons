

import ctypes
import numpy as np
from OpenGL.GL import *  # type: ignore
import pygame

from engine.common import load_texture
from engine.graphics.renderer import Renderer
from game.consts import BLOCK_SIZE
from game.enums.weapon_enum import WeaponEnum
from game.systems.float_rect import FloatRect


class Weapon:
    def __init__(
        self,
        image_shader,
        image_path: str,
        position: tuple[float, float],
        type: WeaponEnum,
        flip_x: bool = False,
        flip_y: bool = True
    ) -> None:

        self.__shader = image_shader
        self.__renderer = Renderer()

        self.__type = type
        self.__texture, ratio = load_texture(image_path)

        self.__width = BLOCK_SIZE * ratio[0]
        self.__height = BLOCK_SIZE * ratio[1]
        x = 0
        y = 0

        self.rect = FloatRect(*position, self.__width, self.__height)

        u0, u1 = (1.0, 0.0) if flip_x else (0.0, 1.0)
        v0, v1 = (1.0, 0.0) if flip_y else (0.0, 1.0)

        vertices = np.array([
            x, y, u0, v0,
            x + self.__width, y, u1, v0,
            x + self.__width, y + self.__height, u1, v1,
            x, y + self.__height, u0, v1,
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

    def draw(self) -> None:
        self.__renderer.draw_texture(
            self.rect.topleft, self.__vao, self.__shader,
            self.__uPlayerPos, self.__uIsPlayer,
            self.__uUseTexture, self.__uTexture,
            self.__texture, self.__uColor
        )

    def get_type(self) -> WeaponEnum:
        return self.__type
