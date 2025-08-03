import pygame
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, IS_DEBUG, ENEMY_SPEED
from float_rect import FloatRect
from game_field import GameField
from physics import Physics


class Enemy:
    def __init__(
        self,
        game_field: GameField,
        start_pos: tuple[int, int],
        moving_start: int,
        moving_end: int
    ) -> None:

        size = BLOCK_SIZE
        self.rect = FloatRect(*start_pos, size, size)
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__direction = ""
        self.__moving_start = moving_start
        self.__moving_end = moving_end

        self.velocity_y = 0.0
        self.max_velocity_y = 50.0
        self.speed = ENEMY_SPEED

    def __draw_square(self, x: float, y: float, color: tuple[float, float, float] = (1, 0, 0), size: int = 4) -> None:
        half = size / 2
        glColor3f(color[0], color[1], color[2])
        glVertex2f(x - half, y - half)
        glVertex2f(x + half, y - half)
        glVertex2f(x + half, y + half)
        glVertex2f(x - half, y + half)

    def update(self) -> None:
        direction_sign = 1 if self.__moving_end > self.__moving_start else -1

        if direction_sign == 1:
            if self.rect.left <= self.__moving_start:
                self.__direction = "right"  # todo: replace strings with enum or boolean (is_left?)
            elif self.rect.right >= self.__moving_end:
                self.__direction = "left"
        else:
            if self.rect.right >= self.__moving_start:
                self.__direction = "left"
            elif self.rect.left <= self.__moving_end:
                self.__direction = "right"

        if self.__direction == "right":
            self.rect.x += self.speed
        elif self.__direction == "left":
            self.rect.x -= self.speed

        self.__physics.gravitation()
        self.__physics.borders_teleportation()

    def draw(self) -> None:

        if IS_DEBUG:
            glColor3f(1, 1, 0)
            glVertex2f(self.rect.x - 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y + self.rect.h + 1)
            glVertex2f(self.rect.x - 1, self.rect.y + self.rect.h + 1)

            self.__draw_square(self.rect.x, self.rect.y, (0 / 255, 255 / 255, 0 / 255))

            point1, point2 = self.__physics.collidepoints("right")
            self.__draw_square(*point1, (255 / 255, 123 / 255, 0 / 255))   # todo: convert colors to constants.
            self.__draw_square(*point2, (255 / 255, 123 / 255, 0 / 255))

            point1, point2 = self.__physics.collidepoints("left")
            self.__draw_square(*point1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(*point2, (255 / 255, 123 / 255, 0 / 255))

            point1, point2 = self.__physics.collidepoints("top")
            self.__draw_square(*point1)
            self.__draw_square(*point2)

            point1, point2 = self.__physics.collidepoints("bottom")
            self.__draw_square(*point1)
            self.__draw_square(*point2)

        glColor3f(1, 0.2, 0.2)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y + self.rect.h)
        glVertex2f(self.rect.x, self.rect.y + self.rect.h)
