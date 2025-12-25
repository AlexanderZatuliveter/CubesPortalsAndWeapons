import numpy as np
import json

from game.entities.block import Block
from game.enums.direction_enum import DirectionEnum
from game.systems.float_rect import FloatRect
from game.systems.position import IntPosition
from game.consts import BLOCK_SIZE


class GameField:
    def __init__(self, x: int, y: int, shader) -> None:
        self.field = np.zeros(shape=(x, y), dtype=object)
        self.field.fill(None)

        self.__shader = shader

    def draw(self) -> None:
        for (bx, by), block in np.ndenumerate(self.field):
            if block:
                pos = self._get_block_position(bx, by)
                block.set_offset(pos[0], pos[1])
                block.draw()

    def _get_block_position(self, bx: int, by: int) -> tuple[float, float]:
        return (
            bx * BLOCK_SIZE,
            by * BLOCK_SIZE
        )

    def get_block_field_position(self, x: float, y: float) -> IntPosition:
        return IntPosition(
            int(x // BLOCK_SIZE),
            int(y // BLOCK_SIZE)
        )

    def _get_block_rect(self, x: int, y: int) -> FloatRect:
        return FloatRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)

    def colliderect_with(self, x: float, y: float, rect: FloatRect) -> bool:
        block_pos = self.get_block_field_position(x, y)

        if 0 <= block_pos.x < len(self.field) and 0 <= block_pos.y < len(self.field[0]):
            block = self.field[block_pos.x][block_pos.y]
            if block and rect.colliderect(self._get_block_rect(block_pos.x, block_pos.y)):
                return True

        return False

    def vertical_block_distance(
        self,
        rightx: float,
        leftx: float,
        bottomy: float,
        topy: float,
        direction: DirectionEnum
    ) -> float:

        if direction == DirectionEnum.UP or direction == DirectionEnum.DOWN:
            distance = 0

            if direction == DirectionEnum.DOWN:
                y = bottomy
            else:
                y = topy

            while True:
                # Получаем индексы блоков по обеим границам
                pos1 = self.get_block_field_position(leftx, y)
                pos2 = self.get_block_field_position(rightx, y)

                # Проверка выхода за границы поля
                out1 = not (0 <= pos1.x < self.field.shape[0] and 0 <= pos1.y < self.field.shape[1])
                out2 = not (0 <= pos2.x < self.field.shape[0] and 0 <= pos2.y < self.field.shape[1])
                if out1 and out2:
                    return float('inf')

                # Проверка наличия блока
                block1 = self.field[pos1.x][pos1.y] if not out1 else None
                block2 = self.field[pos2.x][pos2.y] if not out2 else None
                if block1 or block2:
                    return distance

                distance += 0.1

                if direction == DirectionEnum.DOWN:
                    y += 0.1
                else:
                    y -= 0.1

        return 0

    def horizontal_block_distance(
        self,
        rightx: float,
        leftx: float,
        bottomy: float,
        topy: float,
        direction: DirectionEnum
    ) -> float:

        if direction == DirectionEnum.RIGHT or direction == DirectionEnum.LEFT:
            distance = 0

            if direction == DirectionEnum.RIGHT:
                x = rightx
            else:
                x = leftx

            while True:
                # Получаем индексы блоков по обеим границам
                pos1 = self.get_block_field_position(x, bottomy - 2.0)
                pos2 = self.get_block_field_position(x, topy + 2.0)

                # Проверка выхода за границы поля
                out1 = not (0 <= pos1.x < self.field.shape[0] and 0 <= pos1.y < self.field.shape[1])
                out2 = not (0 <= pos2.x < self.field.shape[0] and 0 <= pos2.y < self.field.shape[1])
                if out1 and out2:
                    return float('inf')

                # Проверка наличия блока
                block1 = self.field[pos1.x][pos1.y] if not out1 else None
                block2 = self.field[pos2.x][pos2.y] if not out2 else None
                if block1 or block2:
                    return distance

                distance += 0.1

                if direction == DirectionEnum.RIGHT:
                    x += 0.1
                else:
                    x -= 0.1
        return 0

    def put_block_by_screen_pos(self, x: int, y: int) -> None:
        pos = self.get_block_field_position(x, y)
        self.put_block(pos)

    def put_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if not block:
            self.field[pos.x][pos.y] = Block(self.__shader)

    def hit_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if block:
            self.field[pos.x][pos.y] = None

    def hit_block_by_screen_pos(self, x, y) -> None:
        pos = self.get_block_field_position(x, y)
        self.hit_block(pos)

    def save_to_file(self) -> None:
        map = {}
        positions = {}
        for (x, y), block in np.ndenumerate(self.field):
            if isinstance(block, Block):
                positions[str(IntPosition(x, y))] = type(block).__name__
        map["positions"] = positions
        json_string = json.dumps(map, indent=2)
        with open("./maps/first.map", "w") as json_file:
            json_file.write(json_string)

    def load_from_file(self) -> None:
        with open("src/_content/maps/first.map", "r") as json_file:
            json_string = json_file.read()

        map_data = json.loads(json_string)

        # Initialize or clear the field
        self.field = np.empty_like(self.field)

        # Access the "positions" dictionary within the loaded map_data
        positions = map_data.get("positions", {})

        for pos_str, block_type in positions.items():
            # Convert pos_str back to an IntPosition instance
            pos = IntPosition.from_string(pos_str)
            self.put_block(pos)
