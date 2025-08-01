from typing import Literal
import pygame
from pygame.key import ScancodeWrapper
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, IS_DEBUG, ENEMY_JUMP_FORCE, ENEMY_SPEED, GRAVITY
from game_field import GameField
from player import Player


class Enemy:
    def __init__(
        self,
        game_field: GameField,
        player: Player,
        start_pos: tuple[int, int],
        moving_start: int,
        moving_end: int
    ) -> None:

        size = BLOCK_SIZE
        self.__rect = pygame.Rect(*start_pos, size, size)
        self.__game_field = game_field

        self.__direction = "right"
        self.__moving_start = moving_start
        self.__moving_end = moving_end

        self.__velocity_y = 0
        self.__max_velocity_y = 50
        self.__gravity = GRAVITY
        self.__speed = ENEMY_SPEED

    def __modify_rect(self, difx: int, dify: int, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(difx + rect.x, dify + rect.y, rect.width, rect.height)

    def __draw_square(
        self,
        x: int,
        y: int,
        color: tuple[float, float, float] = (255 / 255, 0 / 255, 0 / 255),
        size: int = 4
    ) -> None:

        dif = size / 2

        glColor3f(color[0], color[1], color[2])
        glVertex2f(x - dif, y - dif)
        glVertex2f(x + dif, y - dif)
        glVertex2f(x + dif, y + dif)
        glVertex2f(x - dif, y + dif)

    def __collidepoints(self, direction: Literal["bottom", "top", "left", "right"]) -> tuple[int, int, int]:
        if direction == "bottom":
            x1 = self.__rect.x
            x2 = self.__rect.x + self.__rect.width
            y = int(self.__rect.y + self.__rect.height + self.__velocity_y)
            return x1, x2, y
        elif direction == "top":
            x1 = self.__rect.x
            x2 = self.__rect.x + self.__rect.width
            y = self.__rect.y - 7
            return x1, x2, y
        elif direction == "left":
            x = self.__rect.x - self.__speed
            y1 = self.__rect.y + 2
            y2 = self.__rect.y + self.__rect.height - 2
            return x, y1, y2
        elif direction == "right":
            x = self.__rect.x + self.__rect.width + self.__speed
            y1 = self.__rect.y + 2
            y2 = self.__rect.y + self.__rect.height - 2
            return x, y1, y2

    def update(self) -> None:

        x, y1, y2 = self.__collidepoints("left")
        rect = self.__modify_rect(-self.__speed, 0, self.__rect)
        is_left_block = not self.__game_field.colliderect_with(x, y1, rect) \
            and not self.__game_field.colliderect_with(x, y2, rect)

        x, y1, y2 = self.__collidepoints("right")
        rect = self.__modify_rect(self.__speed, 0, self.__rect)
        is_right_block = not self.__game_field.colliderect_with(x, y1, rect) \
            and not self.__game_field.colliderect_with(x, y2, rect)

        x1, x2, y = self.__collidepoints("bottom")
        rect = self.__modify_rect(0, int(self.__velocity_y), self.__rect)
        is_bottom_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        x1, x2, y = self.__collidepoints("top")
        rect = self.__modify_rect(0, -7, self.__rect)
        is_upper_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        if self.__rect.left <= self.__moving_start:
            self.__direction = "right"
        elif self.__rect.right >= self.__moving_end:
            self.__direction = "left"

        if self.__direction == "right":
            self.__rect.x += self.__speed
        elif self.__direction == "left":
            self.__rect.x -= self.__speed

        if is_upper_block:
            self.__velocity_y = 3

        if not is_bottom_block:
            if self.__velocity_y < self.__max_velocity_y:
                self.__velocity_y += self.__gravity
            self.__rect.centery += int(self.__velocity_y)

        if self.__rect.left < 0:
            self.__rect.x = GAME_FIELD_WIDTH - self.__rect.width
        elif self.__rect.right > GAME_FIELD_WIDTH:
            self.__rect.x = 0
        elif self.__rect.bottom > GAME_FIELD_HEIGHT:
            self.__rect.y = 0
        elif self.__rect.top < 0:
            self.__rect.y = GAME_FIELD_HEIGHT - self.__rect.height

    def draw(self) -> None:

        if IS_DEBUG:
            glColor3f(1, 1, 0)
            glVertex2f(self.__rect.x - 1, self.__rect.y - 1)
            glVertex2f(self.__rect.x + self.__rect.w + 1, self.__rect.y - 1)
            glVertex2f(self.__rect.x + self.__rect.w + 1, self.__rect.y + self.__rect.h + 1)
            glVertex2f(self.__rect.x - 1, self.__rect.y + self.__rect.h + 1)

            self.__draw_square(self.__rect.x, self.__rect.y, (0 / 255, 255 / 255, 0 / 255))

            rx, ry1, ry2 = self.__collidepoints("right")
            self.__draw_square(rx, ry1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(rx, ry2, (255 / 255, 123 / 255, 0 / 255))

            lx, ly1, ly2 = self.__collidepoints("left")
            self.__draw_square(lx, ly1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(lx, ly2, (255 / 255, 123 / 255, 0 / 255))

            tx1, tx2, ty = self.__collidepoints("top")
            self.__draw_square(tx1, ty)
            self.__draw_square(tx2, ty)

            bx1, bx2, by = self.__collidepoints("bottom")
            self.__draw_square(bx1, by)
            self.__draw_square(bx2, by)

        glColor3f(235 / 255, 50 / 255, 50 / 255)
        glVertex2f(self.__rect.x, self.__rect.y)
        glVertex2f(self.__rect.x + self.__rect.w, self.__rect.y)
        glVertex2f(self.__rect.x + self.__rect.w, self.__rect.y + self.__rect.h)
        glVertex2f(self.__rect.x, self.__rect.y + self.__rect.h)
