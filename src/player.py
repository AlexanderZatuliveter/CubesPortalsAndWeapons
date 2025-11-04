import numpy
import pygame
from OpenGL.GL import *  # type: ignore
from common import ortho, translate
from consts import BLOCK_HEIGHT, BLOCK_WIDTH, CHANGE_ANTI_GRAVITY, GAME_FIELD_MAX, GAME_FIELD_MIN, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_SPEED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics
from pygame.key import ScancodeWrapper


class Player:
    def __init__(
        self,
        game_field: GameField,
        color: tuple[int, int, int],
        shader,
        joystick_num: int = 1
    ) -> None:

        start_x = 0.9
        start_y = 0.9
        self.rect = FloatRect(start_x, start_y, BLOCK_WIDTH, BLOCK_HEIGHT)

        self.__color = color

        vertices = [
            start_x, start_y, 0.0, *self.__color,
            start_x + BLOCK_WIDTH, start_y, 0.0, *self.__color,
            start_x + BLOCK_WIDTH, start_y + BLOCK_HEIGHT, 0.0, *self.__color,
            start_x, start_y + BLOCK_HEIGHT, 0.0, *self.__color
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

        # Uniform
        self.__uMVP_loc = glGetUniformLocation(shader, "uMVP")
        # Projection (static, camera doesn’t move)
        self.__projection = ortho(
            GAME_FIELD_MIN,
            GAME_FIELD_MAX,
            GAME_FIELD_MIN,
            GAME_FIELD_MAX,
            -1.0,
            1.0
        )

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        try:
            self.__joystick = pygame.joystick.Joystick(joystick_num)
        except BaseException:
            self.__joystick = None

        self.velocity_y = 0.0
        self.max_velocity_y = 25.0
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY

        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__jumping = False

    def update(self, keys: ScancodeWrapper) -> None:

        if self.__joystick:
            # left stick x
            axis_x = self.__joystick.get_axis(0)

            dead_zone = 0.3
            if abs(axis_x) < dead_zone:
                axis_x = 0

            difx = axis_x * self.speed

            if difx < 0:
                if not self.__physics.is_block(DirectionEnum.LEFT):
                    self.rect.x += axis_x * self.speed
            else:
                if not self.__physics.is_block(DirectionEnum.RIGHT):
                    self.rect.x += axis_x * self.speed
        else:
            if keys[pygame.K_RIGHT]:
                if not self.__physics.is_block(DirectionEnum.LEFT):
                    self.rect.x += self.speed
            if keys[pygame.K_LEFT]:
                if not self.__physics.is_block(DirectionEnum.RIGHT):
                    self.rect.x -= self.speed

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP)

        if self.__joystick:
            if self.__joystick.get_button(0) and is_bottom_block and not is_upper_block:
                self.velocity_y = self.__jump_force
                self.__jumping = True

            if not self.__joystick.get_button(0):
                self.__jumping = False
                self.anti_gravity = 0

            if self.__jumping and self.__joystick.get_button(0) and self.velocity_y < 0:
                if self.anti_gravity < self.__max_anti_gravity:
                    self.anti_gravity += self.__change_anti_gravity
        else:
            if keys[pygame.K_UP] and is_bottom_block and not is_upper_block:
                self.velocity_y = self.__jump_force
                self.__jumping = True

            if not keys[pygame.K_UP]:
                self.__jumping = False
                self.anti_gravity = 0

            if self.__jumping and keys[pygame.K_UP] and self.velocity_y < 0:
                if self.anti_gravity < self.__max_anti_gravity:
                    self.anti_gravity += self.__change_anti_gravity

        if self.__jumping == True and self.anti_gravity > 0:
            self.anti_gravity -= 0.005

        # self.__physics.gravitation()
        self.__physics.borders_teleportation()

        print(f"player_x={self.rect.x}; player_y={self.rect.y}")

    def draw(self):
        # Compute matrices
        model = translate(self.rect.x, self.rect.y, 0.0)
        mvp = self.__projection @ model  # (View = identity)
        glUniformMatrix4fv(self.__uMVP_loc, 1, GL_FALSE, mvp)

        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
