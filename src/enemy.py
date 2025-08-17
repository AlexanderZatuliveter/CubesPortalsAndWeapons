from OpenGL.GL import *  # type: ignore
from common import debug_draw_square
from consts import BLOCK_SIZE, CHANGE_ANTI_GRAVITY, IS_DEBUG, ENEMY_SPEED, MAX_ANTI_GRAVITY, RED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics
from renderer import Renderer


class Enemy:
    def __init__(
        self,
        game_field: GameField,
        renderer: Renderer,
        start_pos: tuple[float, float],
        moving_start: float,
        moving_end: float
    ) -> None:

        size = BLOCK_SIZE
        start_pos = start_pos[0] * BLOCK_SIZE, start_pos[1] * BLOCK_SIZE
        self.rect = FloatRect(*start_pos, size, size)

        self.__renderer = renderer
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__direction: DirectionEnum
        self.__moving_start = moving_start * BLOCK_SIZE
        self.__moving_end = moving_end * BLOCK_SIZE

        self.velocity_y = 0.0
        self.max_velocity_y = 50.0
        self.speed = ENEMY_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY

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
        self.__renderer.add_outline(self.rect.x, self.rect.y, self.rect.width, RED)

        if IS_DEBUG:
            debug_draw_square(self.rect.x, self.rect.y, self.rect.width, self.__physics, self.__renderer)
