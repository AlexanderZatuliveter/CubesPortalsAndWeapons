

from consts import BLOCK_HEIGHT, BLOCK_WIDTH, GAME_FIELD_MAX, GAME_FIELD_MIN, GRAVITY
from direction_enum import DirectionEnum

from object_protocol import ObjectProtocol


class Physics:
    def __init__(self, object: ObjectProtocol, game_field) -> None:
        self.__object = object
        self.__game_field = game_field

    def collidepoints(self, direction: DirectionEnum) -> tuple[tuple[float, float], tuple[float, float]]:

        if direction == DirectionEnum.DOWN:
            x1 = self.__object.rect.x + BLOCK_WIDTH / 4
            x2 = self.__object.rect.x + self.__object.rect.width - BLOCK_WIDTH / 4
            y1 = y2 = self.__object.rect.y + self.__object.rect.height + self.__object.velocity_y
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.UP:
            x1 = self.__object.rect.x + BLOCK_WIDTH / 4
            x2 = self.__object.rect.x + self.__object.rect.width - BLOCK_WIDTH / 4
            y1 = y2 = self.__object.rect.y + self.__object.velocity_y
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.LEFT:
            x1 = x2 = self.__object.rect.x - self.__object.speed
            y1 = self.__object.rect.y + BLOCK_HEIGHT / 4
            y2 = self.__object.rect.y + self.__object.rect.height - BLOCK_HEIGHT / 4
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.RIGHT:
            x1 = x2 = self.__object.rect.x + self.__object.rect.width + self.__object.speed
            y1 = self.__object.rect.y + BLOCK_HEIGHT / 4
            y2 = self.__object.rect.y + self.__object.rect.height - BLOCK_HEIGHT / 4
            return ((x1, y1), (x2, y2))

    def is_block(self, direction: DirectionEnum) -> bool:

        if direction == DirectionEnum.DOWN:
            point1, point2 = self.collidepoints(direction)
            rect = self.__object.rect.move(0, self.__object.velocity_y)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.UP:
            point1, point2 = self.collidepoints(direction)
            rect = self.__object.rect.move(0, self.__object.velocity_y)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.RIGHT:
            point1, point2 = self.collidepoints(direction)
            rect = self.__object.rect.move(self.__object.speed, 0)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.LEFT:
            point1, point2 = self.collidepoints(direction)
            rect = self.__object.rect.move(-self.__object.speed, 0)
            is_block = self.__game_field.colliderect_with(*point1, rect) \
                or self.__game_field.colliderect_with(*point2, rect)

        return is_block

    def borders_teleportation(self) -> None:
        if self.__object.rect.left < GAME_FIELD_MIN:
            self.__object.rect.right = GAME_FIELD_MAX
        elif self.__object.rect.right > GAME_FIELD_MAX:
            self.__object.rect.left = GAME_FIELD_MIN
        elif self.__object.rect.bottom < GAME_FIELD_MIN:
            self.__object.rect.top = GAME_FIELD_MAX
        elif self.__object.rect.top > GAME_FIELD_MAX:
            self.__object.rect.bottom = GAME_FIELD_MIN

    def gravitation(self) -> None:
        is_bottom_block = self.is_block(direction=DirectionEnum.DOWN)

        if is_bottom_block:

            bottom_block_distance = self.__game_field.bottom_block_distance(
                self.__object.rect.left,
                self.__object.rect.right,
                self.__object.rect.bottom
            )

            if bottom_block_distance > 0:
                self.__object.rect.move_ip(0, bottom_block_distance)

            self.__object.velocity_y = 0
        else:
            if self.__object.velocity_y < self.__object.max_velocity_y:
                self.__object.velocity_y += (GRAVITY - self.__object.anti_gravity)

            self.__object.rect.move_ip(0, self.__object.velocity_y)

        is_upper_block = self.is_block(direction=DirectionEnum.UP)

        if is_upper_block:
            self.__object.velocity_y = 0
