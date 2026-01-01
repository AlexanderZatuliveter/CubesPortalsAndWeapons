
import ctypes
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram

from game.consts import BAZOOKA_BULLET_DAMAGE, BAZOOKA_BULLET_HEIGHT, BAZOOKA_BULLET_SPEED, BAZOOKA_BULLET_WIDTH, GAME_FIELD_WIDTH, LASER_GUN_BULLET_DAMAGE, LASER_GUN_BULLET_HEIGHT, LASER_GUN_BULLET_SPEED, LASER_GUN_BULLET_WIDTH, MACHINE_GUN_BULLET_DAMAGE, MACHINE_GUN_BULLET_HEIGHT, MACHINE_GUN_BULLET_SPEED, MACHINE_GUN_BULLET_WIDTH
from game.enums.direction_enum import DirectionEnum
from game.enums.weapon_enum import WeaponEnum
from game.systems.float_rect import FloatRect
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.renderer import Renderer


class Bullet:
    def __init__(self, x: float, y: float, direction: DirectionEnum,
                 color: tuple[float, float, float, float], shader: ShaderProgram, bullet_type: WeaponEnum):

        if bullet_type == WeaponEnum.BAZOOKA:
            self.damage = BAZOOKA_BULLET_DAMAGE
            self.__bullet_speed = BAZOOKA_BULLET_SPEED
            width = BAZOOKA_BULLET_WIDTH
            height = BAZOOKA_BULLET_HEIGHT
            self._type = WeaponEnum.BAZOOKA

        elif bullet_type == WeaponEnum.MACHINE_GUN:
            self.damage = MACHINE_GUN_BULLET_DAMAGE
            self.__bullet_speed = MACHINE_GUN_BULLET_SPEED
            width = MACHINE_GUN_BULLET_WIDTH
            height = MACHINE_GUN_BULLET_HEIGHT
            self._type = WeaponEnum.MACHINE_GUN

        elif bullet_type == WeaponEnum.LASER_GUN:
            self.damage = LASER_GUN_BULLET_DAMAGE
            self.__bullet_speed = LASER_GUN_BULLET_SPEED
            width = LASER_GUN_BULLET_WIDTH
            height = LASER_GUN_BULLET_HEIGHT
            self._type = WeaponEnum.LASER_GUN

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

    def update(self, dt: float):
        if self.__direction == DirectionEnum.LEFT:
            self.rect.x -= self.__bullet_speed * dt
        elif self.__direction == DirectionEnum.RIGHT:
            self.rect.x += self.__bullet_speed * dt

        self.__distance += self.__bullet_speed * dt

        if self.rect.right <= 0.0:
            self.rect.right = GAME_FIELD_WIDTH
        elif self.rect.left >= GAME_FIELD_WIDTH:
            self.rect.left = 0.0

        # if self.__distance >= self.__max_distance:
        #     self.__is_destroyed = True

    def is_destroyed(self):
        return self.__is_destroyed

    def draw(self) -> None:
        self.__renderer.draw_square(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, self.rect, self._color,
            self.__vertex_count
        )
