

import numpy
import ctypes
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
from consts import BULLET_HEIGHT, BULLET_SPEED, BULLET_WIDTH, GAME_FIELD_WIDTH
from direction_enum import DirectionEnum
from float_rect import FloatRect


class Bullet:
    def __init__(self, x: float, y: float, direction: DirectionEnum,
                 color: tuple[float, float, float], shader: ShaderProgram):
        self.rect = FloatRect(x, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.color = color
        self.__distance = 0.0
        self.__max_distance = GAME_FIELD_WIDTH * 2
        self.__direction = direction
        self.__is_destroyed = False

        vertices = numpy.array([
            0.0, 0.0,
            BULLET_WIDTH, 0.0,
            BULLET_WIDTH, BULLET_HEIGHT,
            0.0, BULLET_HEIGHT,
        ], dtype=numpy.float32)

        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        self.__uPlayerPos = glGetUniformLocation(shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(shader, "uColor")

    def update(self):
        if self.__direction == DirectionEnum.LEFT:
            self.rect.x -= BULLET_SPEED
        elif self.__direction == DirectionEnum.RIGHT:
            self.rect.x += BULLET_SPEED

        self.__distance += BULLET_SPEED

        if self.rect.right <= 0.0:
            self.rect.right = GAME_FIELD_WIDTH
        elif self.rect.left >= GAME_FIELD_WIDTH:
            self.rect.left = 0.0

        if self.__distance >= self.__max_distance:
            self.__is_destroyed = True

    def is_destroyed(self):
        return self.__is_destroyed

    def draw(self):
        glBindVertexArray(self.__vao)
        glUniform1i(self.__uIsPlayer, 1)
        glUniform2f(self.__uPlayerPos, self.rect.x, self.rect.y)
        glUniform3f(self.__uColor, *self.color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)
