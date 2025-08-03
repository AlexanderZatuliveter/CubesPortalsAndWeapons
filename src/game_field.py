import numpy as np
import pygame
from block import Block
from position import IntPosition
import json
from consts import BLOCK_SIZE


class GameField:
    def __init__(self, x: int, y: int) -> None:
        self.field = np.zeros(shape=(x, y), dtype=object)
        self.field.fill(None)

    def draw(self) -> None:
        for (bx, by), block in np.ndenumerate(self.field):
            if block:
                pos = self._get_block_position(bx, by)
                block.draw(pos)

    def _get_block_position(self, bx: int, by: int) -> tuple[int, int]:
        return (
            bx * BLOCK_SIZE,
            by * BLOCK_SIZE
        )

    def get_block_field_position(self, x: float, y: float) -> IntPosition:
        return IntPosition(
            int(x // BLOCK_SIZE),
            int(y // BLOCK_SIZE)
        )

    def _get_block_rect(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)

    def colliderect_with(self, x: float, y: float, rect: pygame.Rect) -> bool:
        block_pos = self.get_block_field_position(x, y)

        if 0 <= block_pos.x < len(self.field) and 0 <= block_pos.y < len(self.field[0]):
            block = self.field[block_pos.x][block_pos.y]
            if block and rect.colliderect(self._get_block_rect(block_pos.x, block_pos.y)):
                return True

        return False

    def put_block_by_screen_pos(self, x: int, y: int) -> None:
        pos = self.get_block_field_position(x, y)
        self.put_block(pos)

    def put_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if not block:
            self.field[pos.x][pos.y] = Block()

    def hit_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if block:
            self.field[pos.x][pos.y] = None

    def hit_block_by_screen_pos(self, x, y) -> None:
        pos = self.get_block_field_position(x, y)
        self.hit_block(pos)

    # def is_block_on_pos(self, x: int, y: int) -> bool:
    #     block_pos = self.get_block_field_position(x, y)
    #     return self.field[block_pos.x][block_pos.y] is not None

    def save_to_file(self) -> None:
        map = {}
        positions = {}
        for (x, y), block in np.ndenumerate(self.field):
            if isinstance(block, Block):
                positions[str(IntPosition(x, y))] = type(block).__name__
        map["positions"] = positions
        json_string = json.dumps(map, indent=2)
        with open("first.map", "w") as json_file:
            json_file.write(json_string)

    def load_from_file(self) -> None:
        with open("first.map", "r") as json_file:
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
