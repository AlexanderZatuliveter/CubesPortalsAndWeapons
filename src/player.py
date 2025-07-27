from typing import Literal
import pygame
from pygame.key import ScancodeWrapper
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, PLAYER_JUMP_FORCE, PLAYER_SPEED, GRAVITY
from game_field import GameField


class Player:
    def __init__(self, game_field: GameField) -> None:
        size = BLOCK_SIZE
        start_pos = BLOCK_SIZE * 26 / 2, GAME_FIELD_HEIGHT - 144
        self.__rect = pygame.Rect(*start_pos, size, size)
        self.__game_field = game_field

        self.__velocity_y = 0
        self.__gravity = GRAVITY
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__speed = PLAYER_SPEED

    def __modify_rect(self, difx: int, dify: int, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(difx + rect.x, dify + rect.y, rect.width, rect.height)

    def __draw_square(self, x: int, y: int, color: tuple[float, float, float] = (255 / 255, 0 / 255, 0 / 255)) -> None:
        glColor3f(color[0], color[1], color[2])
        glVertex2f(x - 5, y - 5)
        glVertex2f(x + 5, y - 5)
        glVertex2f(x + 5, y + 5)
        glVertex2f(x - 5, y + 5)

    def __collidepoints(self, direction: Literal["bottom", "top", "left", "right"]) -> tuple[int, int, int]:
        if direction == "bottom":
            x1 = self.__rect.x
            x2 = self.__rect.x + self.__rect.width
            y = int(self.__rect.y + self.__rect.height + self.__velocity_y)
            return x1, x2, y
        elif direction == "top":
            x1 = self.__rect.x
            x2 = self.__rect.x + self.__rect.width
            y = self.__rect.y - 5
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

    def update(self, keys: ScancodeWrapper) -> None:
        self.__draw_square(self.__rect.x, self.__rect.y, (0 / 255, 255 / 255, 0 / 255))

        if keys[pygame.K_a] and self.__rect.left > 0:
            x, y1, y2 = self.__collidepoints("left")
            rect = self.__modify_rect(-self.__speed, 0, self.__rect)
            if not self.__game_field.colliderect_with(
                    x, y1, rect) and not self.__game_field.colliderect_with(x, y2, rect):
                self.__rect.centerx -= PLAYER_SPEED

            self.__draw_square(x, y1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(x, y2, (255 / 255, 123 / 255, 0 / 255))

        if keys[pygame.K_d] and self.__rect.right < GAME_FIELD_WIDTH:
            x, y1, y2 = self.__collidepoints("right")
            rect = self.__modify_rect(self.__speed, 0, self.__rect)
            if not self.__game_field.colliderect_with(
                    x, y1, rect) and not self.__game_field.colliderect_with(x, y2, rect):
                self.__rect.centerx += PLAYER_SPEED

            self.__draw_square(x, y1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(x, y2, (255 / 255, 123 / 255, 0 / 255))

        x1, x2, y = self.__collidepoints("bottom")
        rect = self.__modify_rect(0, int(self.__velocity_y), self.__rect)
        is_bottom_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        self.__draw_square(x1, y)
        self.__draw_square(x2, y)

        x1, x2, y = self.__collidepoints("top")
        rect = self.__modify_rect(0, -5, self.__rect)
        is_upper_block = self.__game_field.colliderect_with(x1, y, rect) or \
            self.__game_field.colliderect_with(x2, y, rect)

        self.__draw_square(x1, y)
        self.__draw_square(x2, y)

        is_jump = (is_bottom_block or self.__rect.bottom >= GAME_FIELD_HEIGHT) \
            and not (is_upper_block and self.__rect.top <= 0)

        jump_pressed = keys[pygame.K_w] and is_jump

        if jump_pressed:
            self.__velocity_y = self.__jump_force

        if not is_bottom_block and not self.__rect.bottom > GAME_FIELD_HEIGHT:
            self.__velocity_y += self.__gravity
            self.__rect.centery += int(self.__velocity_y)
        else:
            # Только сбрасывай скорость, если не было прыжка в этом кадре
            if not jump_pressed:
                self.__velocity_y = 0
            if self.__rect.bottom > GAME_FIELD_HEIGHT:
                self.__rect.bottom = GAME_FIELD_HEIGHT

        if self.__rect.top <= 0 or is_upper_block:
            self.__rect.top = max(self.__rect.top, 0)
            self.__velocity_y = self.__gravity * 2

    def draw(self) -> None:
        glColor3f(50 / 255, 50 / 255, 235 / 255)
        glVertex2f(self.__rect.x, self.__rect.y)
        glVertex2f(self.__rect.x + self.__rect.w, self.__rect.y)
        glVertex2f(self.__rect.x + self.__rect.w, self.__rect.y + self.__rect.h)
        glVertex2f(self.__rect.x, self.__rect.y + self.__rect.h)
