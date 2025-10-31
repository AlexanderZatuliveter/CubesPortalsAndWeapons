import numpy
import pygame
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_HEIGHT, BLOCK_WIDTH, CHANGE_ANTI_GRAVITY, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_SPEED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics


class Player:
    def __init__(
        self,
        game_field: GameField,
        color: tuple[int, int, int],
        joystick_num: int
    ) -> None:

        self.__x = -0.25
        self.__y = -0.8

        self.__color = color

        vertices = [
            self.__x, self.__y, 0.0, *self.__color,
            self.__x + BLOCK_WIDTH, self.__y, 0.0, *self.__color,
            self.__x + BLOCK_WIDTH, self.__y + BLOCK_HEIGHT, 0.0, *self.__color,
            self.__x, self.__y + BLOCK_HEIGHT, 0.0, *self.__color
        ]

        vertices_arr = numpy.array(vertices, dtype=numpy.float32)
        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)

        glBufferData(GL_ARRAY_BUFFER, vertices_arr.nbytes, vertices_arr, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        self.rect = FloatRect(self.__x, self.__y, BLOCK_WIDTH, BLOCK_HEIGHT)

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__joystick = pygame.joystick.Joystick(joystick_num)

        self.velocity_y = 0.0
        self.max_velocity_y = 25.0
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY

        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__jumping = False

    def update(self) -> None:

        # left stick x
        axis_x = self.__joystick.get_axis(0)

        dead_zone = 0.3
        if abs(axis_x) < dead_zone:
            axis_x = 0

        difx = axis_x * self.speed

        if difx < 0:
            if not self.__physics.is_block(DirectionEnum.LEFT):
                self.__x += axis_x * self.speed
        else:
            if not self.__physics.is_block(DirectionEnum.RIGHT):
                self.__x += axis_x * self.speed

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP)

        if self.__joystick.get_button(0) and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force
            self.__jumping = True

        if not self.__joystick.get_button(0):
            self.__jumping = False
            self.anti_gravity = 0

        if self.__jumping and self.__joystick.get_button(0) and self.velocity_y < 0:
            if self.anti_gravity < self.__max_anti_gravity:
                self.anti_gravity += self.__change_anti_gravity

        if self.__jumping == True and self.anti_gravity > 0:
            self.anti_gravity -= 0.005

        self.__physics.gravitation()
        self.__physics.borders_teleportation()

    def draw(self):
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
