

from typing import Literal

import pygame

from consts import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, GRAVITY
from game_field import GameField


class Physics:
    def __init__(self, object, game_field: GameField):
        self.__object = object
        self.__game_field = game_field

    def __modify_rect(self, difx: int, dify: int, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(difx + rect.x, dify + rect.y, rect.width, rect.height)

    def collidepoints(self, direction: Literal["bottom", "top", "left", "right"]) -> tuple[int, int, int]:
        if direction == "bottom":
            x1 = self.__object.rect.x
            x2 = self.__object.rect.x + self.__object.rect.width
            y = int(self.__object.rect.y + self.__object.rect.height + self.__object.velocity_y)
            return x1, x2, y
        elif direction == "top":
            x1 = self.__object.rect.x
            x2 = self.__object.rect.x + self.__object.rect.width
            y = self.__object.rect.y - 7
            return x1, x2, y
        elif direction == "left":
            x = self.__object.rect.x - self.__object.speed
            y1 = self.__object.rect.y + 2
            y2 = self.__object.rect.y + self.__object.rect.height - 2
            return x, y1, y2
        elif direction == "right":
            x = self.__object.rect.x + self.__object.rect.width + self.__object.speed
            y1 = self.__object.rect.y + 2
            y2 = self.__object.rect.y + self.__object.rect.height - 2
            return x, y1, y2

    def is_block(self, direction: Literal["bottom", "top", "left", "right"]) -> bool:

        if direction == "bottom":
            x1, x2, y = self.collidepoints(direction)
            rect = self.__modify_rect(0, int(self.__object.velocity_y), self.__object.rect)
            is_block = self.__game_field.colliderect_with(x1, y, rect) or \
                self.__game_field.colliderect_with(x2, y, rect)

        elif direction == "top":
            x1, x2, y = self.collidepoints(direction)
            rect = self.__modify_rect(0, -7, self.__object.rect)
            is_block = self.__game_field.colliderect_with(x1, y, rect) or \
                self.__game_field.colliderect_with(x2, y, rect)

        elif direction == "right":
            x, y1, y2 = self.collidepoints(direction)
            rect = self.__modify_rect(self.__object.speed, 0, self.__object.rect)
            is_block = self.__game_field.colliderect_with(x, y1, rect) or \
                self.__game_field.colliderect_with(x, y2, rect)

        elif direction == "left":
            x, y1, y2 = self.collidepoints(direction)
            rect = self.__modify_rect(-self.__object.speed, 0, self.__object.rect)
            is_block = self.__game_field.colliderect_with(x, y1, rect) \
                or self.__game_field.colliderect_with(x, y2, rect)

        return is_block

    def borders_teleportation(self) -> None:
        if self.__object.rect.left < 0:
            self.__object.rect.right = GAME_FIELD_WIDTH
        elif self.__object.rect.right > GAME_FIELD_WIDTH:
            self.__object.rect.left = 0
        elif self.__object.rect.bottom > GAME_FIELD_HEIGHT:
            self.__object.rect.top = 0
        elif self.__object.rect.top < 0:
            self.__object.rect.bottom = GAME_FIELD_HEIGHT

    def gravitation(self) -> None:

        is_bottom_block = self.is_block(direction="bottom")
        is_upper_block = self.is_block(direction="bottom")

        if not is_bottom_block:
            if self.__object.velocity_y < self.__object.max_velocity_y:
                self.__object.velocity_y += GRAVITY
            self.__object.rect.centery += int(self.__object.velocity_y)
        else:
            if not is_bottom_block and is_upper_block:
                self.__object.velocity_y = 0

        if is_upper_block:
            self.__object.velocity_y = 3
