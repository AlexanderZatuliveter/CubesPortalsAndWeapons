import numpy as np
import json
from OpenGL.GL import *  # type: ignore
from block import Block
from float_rect import FloatRect
from position import IntPosition
from consts import BLOCK_HEIGHT, BLOCK_SIZE, BLOCK_WIDTH, DARK_GREY


class GameField:
    def __init__(self, x: int, y: int) -> None:
        self.field = np.zeros(shape=(x, y), dtype=object)
        self.field.fill(None)

    def draw(self) -> None:
        for (bx, by), block in np.ndenumerate(self.field):
            if block:
                block.draw()

    def _get_block_position(self, bx: int, by: int) -> tuple[float, float]:
        """Возвращает позицию блока."""
        x = -1.0 + bx * BLOCK_WIDTH
        y = -0.915 + by * BLOCK_HEIGHT

        return x, y

    def _get_block_rect_pixels(self, x: int, y: int) -> FloatRect:
        """Возвращает прямоугольник блока в пиксельных координатах (для физики/коллизий)."""
        x_px = x * BLOCK_SIZE
        y_px = y * BLOCK_SIZE
        return FloatRect(x_px, y_px, BLOCK_SIZE, BLOCK_SIZE)

    def get_block_field_position(self, x: float, y: float) -> IntPosition:
        """Перевод в индексы поля."""

        return IntPosition(
            int(x // BLOCK_WIDTH),
            int(y // BLOCK_HEIGHT)
        )

    def _get_block_rect(self, x: int, y: int) -> FloatRect:
        """Возвращает прямоугольник блока в OpenGL координатах."""
        x_gl, y_gl = self._get_block_position(x, y)
        return FloatRect(x_gl, y_gl, BLOCK_WIDTH, BLOCK_HEIGHT)

    def colliderect_with(self, x: float, y: float, rect: FloatRect) -> bool:
        block_pos = self.get_block_field_position(x, y)

        if 0 <= block_pos.x < len(self.field) and 0 <= block_pos.y < len(self.field[0]):
            block = self.field[block_pos.x][block_pos.y]
            if block:
                # Compare rects in pixel coordinates (physics uses pixel-based FloatRect)
                block_rect_px = self._get_block_rect_pixels(block_pos.x, block_pos.y)
                if rect.colliderect(block_rect_px):
                    return True

        return False

    def bottom_block_distance(self, rightx: float, leftx: float, bottomy: float) -> float:
        """
        Находит вертикальное расстояние (в OpenGL-координатах) от bottomy
        до ближайшего блока, который находится выше (по возрастанию y)
        в пределах горизонтального диапазона [leftx, rightx].

        Возвращает float('inf'), если над объектом в поле блоков нет.
        Если блок находится так, что пересекает bottomy, возвращает 0.0.
        """
        # Получим индексы колонок, которые покрывает горизонтальный диапазон
        left_idx = self.get_block_field_position(leftx, bottomy).x
        right_idx = self.get_block_field_position(rightx, bottomy).x

        # Нормализуем порядок и лимиты
        if left_idx > right_idx:
            left_idx, right_idx = right_idx, left_idx

        max_x = self.field.shape[0]
        max_y = self.field.shape[1]

        # Если оба индекса вне поля по x — нет блоков в этом диапазоне
        if right_idx < 0 or left_idx >= max_x:
            return float('inf')

        # Обрежем на границы поля
        left_idx = max(0, left_idx)
        right_idx = min(max_x - 1, right_idx)

        # Стартовый индекс по y (поле индексируется целыми ступенями блока)
        start_y_idx = self.get_block_field_position(0.0, bottomy).y
        # Если стартовый индекс ниже нуля, поднимем до 0
        start_y_idx = max(0, start_y_idx)

        # Перебираем вверх по индексам блоков
        for y_idx in range(start_y_idx, max_y):
            for x_idx in range(left_idx, right_idx + 1):
                block = self.field[x_idx][y_idx]
                if block:
                    # Найден блок: вычисляем его верхнюю и нижнюю GL-координаты
                    block_top = -0.915 + y_idx * BLOCK_HEIGHT   # как в _get_block_position
                    block_bottom = block_top - BLOCK_HEIGHT

                    # расстояние от bottomy до нижней границы блока
                    distance = block_bottom - bottomy

                    # если блок пересекает или лежит на bottomy — возвращаем 0
                    if distance <= 0.0:
                        return 0.0
                    return float(distance)

        # Не нашли блоков выше — возвращаем бесконечность
        return float('inf')

    def put_block_by_screen_pos(self, x: float, y: float) -> None:
        pos = self.get_block_field_position(x, y)
        self.put_block(pos)

    def put_block(self, pos: IntPosition) -> None:
        block = self.field[pos.x][pos.y]
        if not block:
            x, y = self._get_block_position(pos.x, pos.y)

            # Поскольку GL-координата y_gl соответствует верхней границе блока,
            # надо вычесть высоту, чтобы получить нижнюю координату при построении вершин.

            y_bottom = y - BLOCK_HEIGHT
            self.field[pos.x][pos.y] = Block(
                vertices=[
                    x, y_bottom, 0.0, *DARK_GREY,
                    x + BLOCK_WIDTH, y_bottom, 0.0, *DARK_GREY,
                    x + BLOCK_WIDTH, y, 0.0, *DARK_GREY,
                    x, y, 0.0, *DARK_GREY
                ]
            )

    def hit_block_by_screen_pos(self, x: float, y: float) -> None:
        pos = self.get_block_field_position(x, y)
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
            self.put_block(pos)
