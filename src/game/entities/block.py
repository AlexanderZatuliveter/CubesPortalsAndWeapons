
from OpenGL.GL import *  # type: ignore

from game.consts import BLOCK_SIZE
from game.systems.float_rect import FloatRect


class Block:
    def __init__(self) -> None:
        self.rect = FloatRect(0.0, 0.0, BLOCK_SIZE, BLOCK_SIZE)
