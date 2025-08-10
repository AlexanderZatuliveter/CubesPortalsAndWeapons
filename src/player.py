import pygame
from pygame.event import Event
from OpenGL.GL import *  # type: ignore
from common import debug_draw_square, draw_square_topleft
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, IS_DEBUG, PLAYER_JUMP_FORCE, PLAYER_SPEED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics


class Player:
    def __init__(self, game_field: GameField, color: tuple[float, float, float], joystick_num: int) -> None:
        size = BLOCK_SIZE
        start_pos = GAME_FIELD_WIDTH // 3, GAME_FIELD_HEIGHT - BLOCK_SIZE * 2 - 10.0
        self.rect = FloatRect(*start_pos, size, size)

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__joystick = pygame.joystick.Joystick(joystick_num)
        self.__color = color

        self.velocity_y = 0.0
        self.max_velocity_y = 25.0
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = 0.025
        self.__change_anti_gravity = 0.05

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
                self.rect.x += axis_x * self.speed
        else:
            if not self.__physics.is_block(DirectionEnum.RIGHT):
                self.rect.x += axis_x * self.speed

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

    def draw(self) -> None:
        draw_square_topleft(self.rect.x, self.rect.y, self.__color, self.rect.width)

        if IS_DEBUG:
            debug_draw_square(self.rect.x, self.rect.y, self.rect.width, self.__physics)
