from OpenGL.GL import *  # type: ignore

from common import draw_square_topleft, draw_square_topleft_outline
from consts import BLOCK_SIZE, DARK_GREY, IS_DEBUG, RED


class Block:
    def __init__(self) -> None:
        ...

    def draw(self, pos: tuple[float, float]) -> None:

        draw_square_topleft(pos[0], pos[1], DARK_GREY, BLOCK_SIZE)

        if IS_DEBUG:
            draw_square_topleft_outline(pos[0], pos[1], RED, BLOCK_SIZE)
