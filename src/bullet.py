

import numpy
import ctypes
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
from bullet_enum import BulletEnum
from consts import BIG_BULLET_DAMAGE, BIG_BULLET_HEIGHT, BIG_BULLET_MAX_DISTANCE, BIG_BULLET_SPEED, BIG_BULLET_WIDTH, GAME_FIELD_WIDTH, SMALL_BULLET_DAMAGE, SMALL_BULLET_HEIGHT, SMALL_BULLET_MAX_DISTANCE, SMALL_BULLET_SPEED, SMALL_BULLET_WIDTH
from direction_enum import DirectionEnum
from float_rect import FloatRect


class Bullet:
    def __init__(self, x: float, y: float, direction: DirectionEnum,
                 color: tuple[float, float, float], shader: ShaderProgram, bullet_type: BulletEnum):

        if bullet_type == BulletEnum.BIG:
            self.damage = BIG_BULLET_DAMAGE
            self.__bullet_speed = BIG_BULLET_SPEED
            self.__max_distance = BIG_BULLET_MAX_DISTANCE
            width = BIG_BULLET_WIDTH
            height = BIG_BULLET_HEIGHT

        elif bullet_type == BulletEnum.SMALL:
            self.damage = SMALL_BULLET_DAMAGE
            self.__bullet_speed = SMALL_BULLET_SPEED
            self.__max_distance = SMALL_BULLET_MAX_DISTANCE
            width = SMALL_BULLET_WIDTH
            height = SMALL_BULLET_HEIGHT

        self.rect = FloatRect(x, y, width, height)
        self.color = color
        self.__distance = 0.0
        self.__direction = direction
        self.__is_destroyed = False

        vertices = numpy.array([
            0.0, 0.0,
            width, 0.0,
            width, height,
            0.0, height,
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
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")

    def update(self):
        if self.__direction == DirectionEnum.LEFT:
            self.rect.x -= self.__bullet_speed
        elif self.__direction == DirectionEnum.RIGHT:
            self.rect.x += self.__bullet_speed

        self.__distance += self.__bullet_speed

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
        glUniform1i(self.__uUseTexture, 0)
        glUniform1i(self.__uIsPlayer, 1)
        glUniform2f(self.__uPlayerPos, self.rect.x, self.rect.y)
        glUniform3f(self.__uColor, *self.color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)
