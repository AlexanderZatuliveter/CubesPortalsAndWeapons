

from typing import Literal

import pygame

from consts import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, GRAVITY
from game_field import GameField
from object_protocol import ObjectProtocol


class Physics:
    # todo: use protocol for object.
    def __init__(self, object: ObjectProtocol, game_field: GameField) -> None:
        self.__object = object
        self.__game_field = game_field

    def __modify_rect(self, difx: float, dify: float, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(difx + rect.x, dify + rect.y, rect.width, rect.height)

    # todo: convert "bottom", "top", "left", "right" to enum.
    def collidepoints(
        self,
        direction: Literal["bottom", "top", "left", "right"]
    ) -> tuple[tuple[float, float], tuple[float, float]]:

        if direction == "bottom":
            x1 = self.__object.rect.x
            x2 = self.__object.rect.x + self.__object.rect.width
            y1 = y2 = int(self.__object.rect.y + self.__object.rect.height + self.__object.velocity_y)
            return ((x1, y1), (x2, y2))
        elif direction == "top":
            x1 = self.__object.rect.x
            x2 = self.__object.rect.x + self.__object.rect.width
            y1 = y2 = self.__object.rect.y - 7
            return ((x1, y1), (x2, y2))
        elif direction == "left":
            x1 = x2 = self.__object.rect.x - self.__object.speed
            y1 = self.__object.rect.y + 2
            y2 = self.__object.rect.y + self.__object.rect.height - 2
            return ((x1, y1), (x2, y2))
        elif direction == "right":
            x1 = x2 = self.__object.rect.x + self.__object.rect.width + self.__object.speed
            y1 = self.__object.rect.y + 2
            y2 = self.__object.rect.y + self.__object.rect.height - 2
            return ((x1, y1), (x2, y2))

    # todo: convert direction to enum:
    def is_block(self, direction: Literal["bottom", "top", "left", "right"]) -> bool:

        if direction == "bottom":
            point1, point2 = self.collidepoints(direction)
            rect = self.__modify_rect(0, int(self.__object.velocity_y), self.__object.rect)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == "top":
            point1, point2 = self.collidepoints(direction)
            rect = self.__modify_rect(0, -7, self.__object.rect)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == "right":
            point1, point2 = self.collidepoints(direction)
            rect = self.__modify_rect(self.__object.speed, 0, self.__object.rect)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == "left":
            point1, point2 = self.collidepoints(direction)
            rect = self.__modify_rect(-self.__object.speed, 0, self.__object.rect)
            is_block = self.__game_field.colliderect_with(*point1, rect) \
                or self.__game_field.colliderect_with(*point2, rect)

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
        is_upper_block = self.is_block(direction="top")

        if not is_bottom_block:
            if self.__object.velocity_y < self.__object.max_velocity_y:
                self.__object.velocity_y += GRAVITY
            self.__object.rect.centery += int(self.__object.velocity_y)
        else:
            if is_bottom_block:
                self.__object.velocity_y = 0

        if is_upper_block:
            self.__object.velocity_y = 5
