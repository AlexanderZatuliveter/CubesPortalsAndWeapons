from OpenGL.GL import *  # type: ignore
from draw_common import debug_draw_square, draw_square_topleft
from consts import BLOCK_SIZE, IS_DEBUG, ENEMY_SPEED, RED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics


class Enemy:
    def __init__(
        self,
        game_field: GameField,
        start_pos: tuple[float, float],
        moving_start: float,
        moving_end: float
    ) -> None:

        size = BLOCK_SIZE
        start_pos = start_pos[0] * BLOCK_SIZE, start_pos[1] * BLOCK_SIZE
        self.rect = FloatRect(*start_pos, size, size)
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__direction: DirectionEnum
        self.__moving_start = moving_start * BLOCK_SIZE
        self.__moving_end = moving_end * BLOCK_SIZE

        self.velocity_y = 0.0
        self.max_velocity_y = 50.0
        self.speed = ENEMY_SPEED

    def update(self) -> None:
        direction_sign = 1 if self.__moving_end > self.__moving_start else -1

        if direction_sign == 1:
            if self.rect.left <= self.__moving_start:
                self.__direction = DirectionEnum.RIGHT
            elif self.rect.right >= self.__moving_end:
                self.__direction = DirectionEnum.LEFT
        else:
            if self.rect.right >= self.__moving_start:
                self.__direction = DirectionEnum.LEFT
            elif self.rect.left <= self.__moving_end:
                self.__direction = DirectionEnum.RIGHT

        if self.__direction == DirectionEnum.RIGHT:
            self.rect.x += self.speed
        elif self.__direction == DirectionEnum.LEFT:
            self.rect.x -= self.speed

        self.__physics.gravitation()
        self.__physics.borders_teleportation()

    def draw(self) -> None:
        draw_square_topleft(self.rect.x, self.rect.y, RED, self.rect.width)

        if IS_DEBUG:
            debug_draw_square(self.rect.x, self.rect.y, self.rect.width, self.__physics)
