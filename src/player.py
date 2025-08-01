from typing import Literal
import pygame
from pygame.key import ScancodeWrapper
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, IS_DEBUG, PLAYER_JUMP_FORCE, PLAYER_SPEED, GRAVITY
from game_field import GameField


class Player:
    def __init__(self, game_field: GameField) -> None:
        size = BLOCK_SIZE
        start_pos = GAME_FIELD_WIDTH // 3, GAME_FIELD_HEIGHT - BLOCK_SIZE * 2
        self.rect = pygame.Rect(*start_pos, size, size)
        self.__game_field = game_field

        self.__velocity_y = 0
        self.__max_velocity_y = 50
        self.__gravity = GRAVITY
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__speed = PLAYER_SPEED

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
            x1 = self.rect.x
            x2 = self.rect.x + self.rect.width
            y = int(self.rect.y + self.rect.height + self.__velocity_y)
            return x1, x2, y
        elif direction == "top":
            x1 = self.rect.x
            x2 = self.rect.x + self.rect.width
            y = self.rect.y - 7
            return x1, x2, y
        elif direction == "left":
            x = self.rect.x - self.__speed
            y1 = self.rect.y + 2
            y2 = self.rect.y + self.rect.height - 2
            return x, y1, y2
        elif direction == "right":
            x = self.rect.x + self.rect.width + self.__speed
            y1 = self.rect.y + 2
            y2 = self.rect.y + self.rect.height - 2
            return x, y1, y2

    def update(self, keys: ScancodeWrapper) -> None:

        if keys[pygame.K_a]:
            x, y1, y2 = self.__collidepoints("left")
            rect = self.__modify_rect(-self.__speed, 0, self.rect)
            if not self.__game_field.colliderect_with(x, y1, rect) \
                    and not self.__game_field.colliderect_with(x, y2, rect):
                self.rect.centerx -= PLAYER_SPEED

        if keys[pygame.K_d]:
            x, y1, y2 = self.__collidepoints("right")
            rect = self.__modify_rect(self.__speed, 0, self.rect)
            if not self.__game_field.colliderect_with(x, y1, rect) \
                    and not self.__game_field.colliderect_with(x, y2, rect):
                self.rect.centerx += PLAYER_SPEED

        x1, x2, y = self.__collidepoints("bottom")
        rect = self.__modify_rect(0, int(self.__velocity_y), self.rect)
        is_bottom_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        x1, x2, y = self.__collidepoints("top")
        rect = self.__modify_rect(0, -7, self.rect)
        is_upper_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        jump_pressed = keys[pygame.K_w] and is_bottom_block and not is_upper_block

        if jump_pressed:
            self.__velocity_y = self.__jump_force

        if not is_bottom_block:
            if self.__velocity_y < self.__max_velocity_y:
                self.__velocity_y += self.__gravity
            self.rect.centery += int(self.__velocity_y)
        else:
            if not jump_pressed:
                self.__velocity_y = 0

        if is_upper_block:
            self.__velocity_y = 3

        if self.rect.left < 0:
            self.rect.x = GAME_FIELD_WIDTH - self.rect.width
        elif self.rect.right > GAME_FIELD_WIDTH:
            self.rect.x = 0
        elif self.rect.bottom > GAME_FIELD_HEIGHT:
            self.rect.y = 0
        elif self.rect.top < 0:
            self.rect.y = GAME_FIELD_HEIGHT - self.rect.height

    def draw(self) -> None:

        if IS_DEBUG:
            glColor3f(1, 1, 0)
            glVertex2f(self.rect.x - 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y + self.rect.h + 1)
            glVertex2f(self.rect.x - 1, self.rect.y + self.rect.h + 1)

            self.__draw_square(self.rect.x, self.rect.y, (0 / 255, 255 / 255, 0 / 255))

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

        glColor3f(50 / 255, 50 / 255, 235 / 255)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y + self.rect.h)
        glVertex2f(self.rect.x, self.rect.y + self.rect.h)
