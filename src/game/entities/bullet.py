
import ctypes
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram

from game.enums.bullet_enum import BulletEnum
from game.consts import BIG_BULLET_DAMAGE, BIG_BULLET_HEIGHT, BIG_BULLET_MAX_DISTANCE, BIG_BULLET_SPEED, BIG_BULLET_WIDTH, GAME_FIELD_WIDTH, SMALL_BULLET_DAMAGE, SMALL_BULLET_HEIGHT, SMALL_BULLET_MAX_DISTANCE, SMALL_BULLET_SPEED, SMALL_BULLET_WIDTH
from game.enums.direction_enum import DirectionEnum
from game.systems.float_rect import FloatRect
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.renderer import Renderer


class Bullet:
    def __init__(self, x: float, y: float, direction: DirectionEnum,
                 color: tuple[float, float, float], shader: ShaderProgram, bullet_type: BulletEnum):

        if bullet_type == BulletEnum.BIG:
            self.damage = BIG_BULLET_DAMAGE
            self.__bullet_speed = BIG_BULLET_SPEED
            self.__max_distance = BIG_BULLET_MAX_DISTANCE
            width = BIG_BULLET_WIDTH
            height = BIG_BULLET_HEIGHT
            self._type = BulletEnum.BIG

        elif bullet_type == BulletEnum.SMALL:
            self.damage = SMALL_BULLET_DAMAGE
            self.__bullet_speed = SMALL_BULLET_SPEED
            self.__max_distance = SMALL_BULLET_MAX_DISTANCE
            width = SMALL_BULLET_WIDTH
            height = SMALL_BULLET_HEIGHT
            self._type = BulletEnum.SMALL

        self.rect = FloatRect(x, y, width, height)
        self._color = color
        self.__distance = 0.0
        self.__direction = direction
        self.__is_destroyed = False

        self.__renderer = Renderer()

        vertices = OpenGLUtils.create_rectangle_vertices(width, height)
        self.__vertex_count = 4
        self.__vao, self.__vbo = self.__renderer.create_vao_vbo(vertices)

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

    def draw(self) -> None:
        self.__renderer.draw_square(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, self.rect, self._color,
            self.__vertex_count
        )
