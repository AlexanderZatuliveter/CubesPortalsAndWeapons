import pygame
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, IS_DEBUG, ENEMY_SPEED
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
        self.rect = pygame.Rect(*start_pos, size, size)
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.__direction = ""
        self.__moving_start = moving_start
        self.__moving_end = moving_end

        self.velocity_y = 0
        self.max_velocity_y = 50
        self.speed = ENEMY_SPEED

    def __draw_square(self, x: int, y: int, color: tuple[float, float, float] = (1, 0, 0), size: int = 4) -> None:
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
                self.__direction = "right"
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

            rx, ry1, ry2 = self.__physics.collidepoints("right")
            self.__draw_square(rx, ry1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(rx, ry2, (255 / 255, 123 / 255, 0 / 255))

            lx, ly1, ly2 = self.__physics.collidepoints("left")
            self.__draw_square(lx, ly1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(lx, ly2, (255 / 255, 123 / 255, 0 / 255))

            tx1, tx2, ty = self.__physics.collidepoints("top")
            self.__draw_square(tx1, ty)
            self.__draw_square(tx2, ty)

            bx1, bx2, by = self.__physics.collidepoints("bottom")
            self.__draw_square(bx1, by)
            self.__draw_square(bx2, by)

        glColor3f(235 / 255, 50 / 255, 50 / 255)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y + self.rect.h)
        glVertex2f(self.rect.x, self.rect.y + self.rect.h)
