
import ctypes
import math
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import pygame

from game.consts import BAZOOKA_BULLET_DAMAGE, BAZOOKA_BULLET_HEIGHT, BAZOOKA_BULLET_SPEED, BAZOOKA_BULLET_WIDTH, BLOCK_SIZE, SHOTGUN_BULLET_DISPERSION_VELOCITY, GAME_FIELD_WIDTH, LASER_GUN_BULLET_DAMAGE, LASER_GUN_BULLET_HEIGHT, MACHINE_GUN_BULLET_DAMAGE, MACHINE_GUN_BULLET_HEIGHT, MACHINE_GUN_BULLET_SPEED, MACHINE_GUN_BULLET_WIDTH, SHOTGUN_BULLET_DAMAGE, SHOTGUN_BULLET_HEIGHT, SHOTGUN_BULLET_SPEED, SHOTGUN_BULLET_WIDTH
from game.enums.direction_enum import DirectionEnum
from game.enums.weapon_enum import WeaponEnum
from game.systems.float_rect import FloatRect
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.renderer import Renderer
from engine.graphics.opengl_utils import OpenGLUtils
from game.systems.rotated_rect import RotatedRect


class Bullet:
    def __init__(
        self,
        x: float,
        y: float,
        direction: DirectionEnum,
        color: tuple[float, float, float, float],
        shader: ShaderProgram,
        type: WeaponEnum,
        angle: float = 0
    ) -> None:

        self.__type = type

        if self.__type == WeaponEnum.BAZOOKA:
            self.damage = BAZOOKA_BULLET_DAMAGE
            self.__bullet_speed = BAZOOKA_BULLET_SPEED
            width = BAZOOKA_BULLET_WIDTH
            height = BAZOOKA_BULLET_HEIGHT
            self._type = WeaponEnum.BAZOOKA

        elif self.__type == WeaponEnum.MACHINE_GUN:
            self.damage = MACHINE_GUN_BULLET_DAMAGE
            self.__bullet_speed = MACHINE_GUN_BULLET_SPEED
            width = MACHINE_GUN_BULLET_WIDTH
            height = MACHINE_GUN_BULLET_HEIGHT
            self._type = WeaponEnum.MACHINE_GUN

        # todo: add shotgun
        elif self.__type == WeaponEnum.SHOTGUN:
            self.damage = SHOTGUN_BULLET_DAMAGE
            self.__bullet_speed = SHOTGUN_BULLET_SPEED
            width = SHOTGUN_BULLET_WIDTH
            height = SHOTGUN_BULLET_HEIGHT
            self._type = WeaponEnum.SHOTGUN

        elif self.__type == WeaponEnum.LASER_GUN:
            self.damage = LASER_GUN_BULLET_DAMAGE
            self.__bullet_speed = 0
            width = GAME_FIELD_WIDTH - BLOCK_SIZE - x
            height = LASER_GUN_BULLET_HEIGHT
            self._type = WeaponEnum.LASER_GUN

        self.rect = FloatRect(x, y, width, height)
        self.__rotated_rect = RotatedRect(self.rect)

        self._color = color
        self.__direction = direction
        self.__angle = angle

        self.__is_destroyed = False
        self.__last_time = pygame.time.get_ticks()

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

        points = self.__rotated_rect.get_points(math.radians(self.__angle))
        vertices = OpenGLUtils.create_vertices_with_points(points)
        self.__vao, self.__vbo = self.__renderer.create_vao_vbo(vertices)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    def update(self, dt: float):
        if self.__type == WeaponEnum.LASER_GUN:
            now = pygame.time.get_ticks()
            if now - self.__last_time >= 10:
                self.__last_time = now
                self.__is_destroyed = True
                return

        if self.__direction == DirectionEnum.LEFT:
            self.rect.x -= self.__bullet_speed * dt
        elif self.__direction == DirectionEnum.RIGHT:
            self.rect.x += self.__bullet_speed * dt

        if self.__type == WeaponEnum.SHOTGUN:
            if self.__direction == DirectionEnum.RIGHT:
                self.rect.y += SHOTGUN_BULLET_DISPERSION_VELOCITY * self.__angle * dt
            else:
                self.rect.y -= SHOTGUN_BULLET_DISPERSION_VELOCITY * self.__angle * dt

        if self.rect.right <= 0.0:
            self.rect.right = GAME_FIELD_WIDTH
        elif self.rect.left >= GAME_FIELD_WIDTH:
            self.rect.left = 0.0

    def is_destroyed(self):
        return self.__is_destroyed

    def draw(self) -> None:
        self.__renderer.draw_square(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, self.rect, self._color,
            self.__vertex_count
        )
