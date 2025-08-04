import pygame
from pygame.key import ScancodeWrapper
from OpenGL.GL import *  # type: ignore
from draw_common import debug_draw_square, draw_square_topleft
from consts import BLOCK_SIZE, BLUE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, IS_DEBUG, PLAYER_JUMP_FORCE, PLAYER_SPEED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics


class Player:
    def __init__(self, game_field: GameField) -> None:
        size = BLOCK_SIZE
        start_pos = GAME_FIELD_WIDTH // 3, GAME_FIELD_HEIGHT - BLOCK_SIZE * 2
        self.rect = FloatRect(*start_pos, size, size)
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.velocity_y = 0.0
        self.max_velocity_y = 50.0
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.speed = PLAYER_SPEED

    def update(self, keys: ScancodeWrapper) -> None:

        if keys[pygame.K_a]:
            if not self.__physics.is_block(DirectionEnum.LEFT):
                self.rect.move_ip(-self.speed, 0)

        if keys[pygame.K_d] and not self.__physics.is_block(DirectionEnum.RIGHT):
            self.rect.move_ip(self.speed, 0)

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP)

        if keys[pygame.K_w] and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force

        self.__physics.gravitation()
        self.__physics.borders_teleportation()

    def draw(self) -> None:
        draw_square_topleft(self.rect.x, self.rect.y, BLUE, self.rect.width)

        if IS_DEBUG:
            debug_draw_square(self.rect.x, self.rect.y, self.rect.width, self.__physics)
