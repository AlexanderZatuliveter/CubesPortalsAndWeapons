from game.consts import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, GRAVITY
from game.enums.direction_enum import DirectionEnum
from game.systems.object_protocol import ObjectProtocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_field import GameField


class Physics:
    def __init__(self, object: ObjectProtocol, game_field: "GameField") -> None:
        self.__object = object
        self.__game_field = game_field

    def collidepoints(self, direction: DirectionEnum, dt: float) -> tuple[tuple[float, float], tuple[float, float]]:

        if direction == DirectionEnum.DOWN:
            x1 = self.__object.rect.x + 2.0
            x2 = self.__object.rect.x + self.__object.rect.width - 2.0
            y1 = y2 = self.__object.rect.y + self.__object.rect.height + self.__object.velocity_y * dt
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.UP:
            x1 = self.__object.rect.x + 2.0
            x2 = self.__object.rect.x + self.__object.rect.width - 2.0
            y1 = y2 = self.__object.rect.y + self.__object.velocity_y * dt
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.LEFT:
            x1 = x2 = self.__object.rect.x - self.__object.speed * dt
            y1 = self.__object.rect.y + 2.0
            y2 = self.__object.rect.y + self.__object.rect.height - 2.0
            return ((x1, y1), (x2, y2))
        elif direction == DirectionEnum.RIGHT:
            x1 = x2 = self.__object.rect.x + self.__object.rect.width + self.__object.speed * dt
            y1 = self.__object.rect.y + 2.0
            y2 = self.__object.rect.y + self.__object.rect.height - 2.0
            return ((x1, y1), (x2, y2))

    def is_block(self, direction: DirectionEnum, dt: float) -> bool:

        if direction == DirectionEnum.DOWN:
            point1, point2 = self.collidepoints(direction, dt)
            rect = self.__object.rect.move(0, self.__object.velocity_y * dt)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.UP:
            point1, point2 = self.collidepoints(direction, dt)
            rect = self.__object.rect.move(0, self.__object.velocity_y * dt)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.RIGHT:
            point1, point2 = self.collidepoints(direction, dt)
            rect = self.__object.rect.move(self.__object.speed * dt, 0)
            is_block = self.__game_field.colliderect_with(*point1, rect) or \
                self.__game_field.colliderect_with(*point2, rect)

        elif direction == DirectionEnum.LEFT:
            point1, point2 = self.collidepoints(direction, dt)
            rect = self.__object.rect.move(-self.__object.speed * dt, 0)
            is_block = self.__game_field.colliderect_with(*point1, rect) \
                or self.__game_field.colliderect_with(*point2, rect)

        return is_block

    def borders_teleportation(self) -> None:
        coefficient = 0.75
        teleport_rect_width = self.__object.rect.width * coefficient
        teleport_rect_height = self.__object.rect.height * coefficient

        if self.__object.rect.left < 0 - teleport_rect_width:
            self.__object.rect.right = GAME_FIELD_WIDTH + teleport_rect_width
        elif self.__object.rect.right > GAME_FIELD_WIDTH + teleport_rect_width:
            self.__object.rect.left = 0 - teleport_rect_width
        elif self.__object.rect.bottom > GAME_FIELD_HEIGHT + teleport_rect_height:
            self.__object.rect.top = 0 - teleport_rect_height
        elif self.__object.rect.top < 0 - teleport_rect_height:
            self.__object.rect.bottom = GAME_FIELD_HEIGHT + teleport_rect_height

    def side_blocks(self, dt: float) -> DirectionEnum | None:

        is_left_block = self.is_block(direction=DirectionEnum.LEFT, dt=dt)
        is_right_block = self.is_block(direction=DirectionEnum.RIGHT, dt=dt)
        is_block = is_left_block or is_right_block

        if is_block:

            if is_left_block:
                direction = DirectionEnum.LEFT
                move_dir = -1
            else:
                direction = DirectionEnum.RIGHT
                move_dir = 1

            block_distance = self.__game_field.horizontal_block_distance(
                self.__object.rect.right,
                self.__object.rect.left,
                self.__object.rect.bottom,
                self.__object.rect.top,
                direction
            )

            if block_distance > 0:
                self.__object.rect.move_ip(move_dir * block_distance, 0)

            return direction

    def gravitation(self, dt: float) -> None:

        is_bottom_block = self.is_block(direction=DirectionEnum.DOWN, dt=dt)

        if is_bottom_block:

            bottom_block_distance = self.__game_field.vertical_block_distance(
                self.__object.rect.left,
                self.__object.rect.right,
                self.__object.rect.bottom,
                self.__object.rect.top,
                direction=DirectionEnum.DOWN
            )

            if bottom_block_distance > 0:
                self.__object.rect.move_ip(0, bottom_block_distance)

            self.__object.velocity_y = 0
        else:
            if self.__object.velocity_y < self.__object.max_velocity_y:
                self.__object.velocity_y += (GRAVITY - self.__object.anti_gravity) * dt

            self.__object.rect.move_ip(0, self.__object.velocity_y * dt)

        is_upper_block = self.is_block(direction=DirectionEnum.UP, dt=dt)

        if is_upper_block:

            upper_block_distance = self.__game_field.vertical_block_distance(
                self.__object.rect.left,
                self.__object.rect.right,
                self.__object.rect.bottom,
                self.__object.rect.top,
                direction=DirectionEnum.UP
            )

            if upper_block_distance > 0:
                self.__object.rect.move_ip(0, -upper_block_distance)

            self.__object.velocity_y = 0
