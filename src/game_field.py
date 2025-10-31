import numpy as np
import json
from OpenGL.GL import *  # type: ignore
from block import Block
from common import to_gl_coords
from float_rect import FloatRect
from position import IntPosition
from consts import BLOCK_SIZE, DARK_GREY, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT


class GameField:
    def __init__(self, x: int, y: int) -> None:
        self.field = np.zeros(shape=(x, y), dtype=object)
        self.field.fill(None)

        # Переводим размер блока в координаты OpenGL
        self.block_width_gl = (BLOCK_SIZE / GAME_FIELD_WIDTH) * 2
        self.block_height_gl = (BLOCK_SIZE / GAME_FIELD_HEIGHT) * 2

    def draw(self) -> None:
        for (bx, by), block in np.ndenumerate(self.field):
            if block:
                # pos = self._get_block_position_gl(bx, by)
                # block.draw(pos)
                block.draw()

    def _get_block_position_gl(self, bx: int, by: int) -> tuple[float, float]:
        """Возвращает позицию блока в OpenGL координатах."""
        x_pixel = bx * BLOCK_SIZE
        y_pixel = by * BLOCK_SIZE

        x_gl, y_gl = to_gl_coords(x_pixel, y_pixel, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT)
        return x_gl, y_gl

    def _get_block_rect_pixels(self, x: int, y: int) -> FloatRect:
        """Возвращает прямоугольник блока в пиксельных координатах (для физики/коллизий)."""
        x_px = x * BLOCK_SIZE
        y_px = y * BLOCK_SIZE
        return FloatRect(x_px, y_px, BLOCK_SIZE, BLOCK_SIZE)

    def get_block_field_position(self, x_gl: float, y_gl: float) -> IntPosition:
        """Перевод из OpenGL координат обратно в индексы поля."""
        # Сначала обратно в пиксели
        x_px = ((x_gl + 1) / 2) * GAME_FIELD_WIDTH
        y_px = ((1 - y_gl) / 2) * GAME_FIELD_HEIGHT

        return IntPosition(
            int(x_px // BLOCK_SIZE),
            int(y_px // BLOCK_SIZE)
        )

    def _get_block_rect(self, x: int, y: int) -> FloatRect:
        """Возвращает прямоугольник блока в OpenGL координатах."""
        x_gl, y_gl = self._get_block_position_gl(x, y)
        return FloatRect(x_gl, y_gl, self.block_width_gl, self.block_height_gl)

    def colliderect_with(self, x_gl: float, y_gl: float, rect: FloatRect) -> bool:
        # get_block_field_position accepts either GL coords (range ~ -1..1) or pixel coords
        block_pos = self.get_block_field_position(x_gl, y_gl)

        if 0 <= block_pos.x < len(self.field) and 0 <= block_pos.y < len(self.field[0]):
            block = self.field[block_pos.x][block_pos.y]
            if block:
                # Compare rects in pixel coordinates (physics uses pixel-based FloatRect)
                block_rect_px = self._get_block_rect_pixels(block_pos.x, block_pos.y)
                if rect.colliderect(block_rect_px):
                    return True

        return False

    def bottom_block_distance(self, rightx: float, leftx: float, bottomy: float) -> float:
        distance = 0
        y = bottomy

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
            y += 0.1

    def put_block_by_screen_pos(self, x_gl: float, y_gl: float) -> None:
        pos = self.get_block_field_position(x_gl, y_gl)
        self.put_block(pos)

    def put_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if not block:
            # Получаем GL-координаты верхнего левого угла блока
            x_gl, y_gl = self._get_block_position_gl(pos.x, pos.y)
            # Поскольку GL-координата y_gl соответствует верхней границе блока,
            # надо вычесть высоту, чтобы получить нижнюю координату при построении вершин.
            y_bottom = y_gl - self.block_height_gl
            self.field[pos.x][pos.y] = Block(
                vertices=[
                    x_gl, y_bottom, 0.0, *DARK_GREY,
                    x_gl + self.block_width_gl, y_bottom, 0.0, *DARK_GREY,
                    x_gl + self.block_width_gl, y_gl, 0.0, *DARK_GREY,
                    x_gl, y_gl, 0.0, *DARK_GREY
                ]
            )

    def hit_block_by_screen_pos(self, x_gl: float, y_gl: float) -> None:
        pos = self.get_block_field_position(x_gl, y_gl)
        self.hit_block(pos)

    def hit_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if block:
            self.field[pos.x][pos.y] = None

    def save_to_file(self) -> None:
        data = {"positions": {}}
        for (x, y), block in np.ndenumerate(self.field):
            if isinstance(block, Block):
                data["positions"][str(IntPosition(x, y))] = type(block).__name__

        with open("first.map", "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self) -> None:
        with open("first.map", "r") as f:
            map_data = json.load(f)

        # Создаём новый пустой массив того же размера, заполненный None,
        # чтобы не оставалось неинициализированных/случайных объектов.
        old_shape = self.field.shape
        self.field = np.zeros(old_shape, dtype=object)
        self.field.fill(None)

        positions = map_data.get("positions", {})

        for pos_str, block_type in positions.items():
            pos = IntPosition.from_string(pos_str)
            # put_block использует GL-координаты внутри себя
            self.put_block(pos)
