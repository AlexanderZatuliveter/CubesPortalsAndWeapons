from typing import Tuple
from OpenGL.GL import *  # type: ignore

from consts import BLOCK_SIZE, DARK_GREY, IS_DEBUG, RED


class Block:
    def __init__(self) -> None:
        ...

    def draw(self, pos: Tuple[int, int]) -> None:
        if IS_DEBUG:
            glColor3f(*RED)
            glVertex2f(pos[0] - 1, pos[1] - 1)
            glVertex2f(pos[0] + BLOCK_SIZE + 1, pos[1] - 1)
            glVertex2f(pos[0] + BLOCK_SIZE + 1, pos[1] + BLOCK_SIZE + 1)
            glVertex2f(pos[0] - 1, pos[1] + BLOCK_SIZE + 1)

        glColor3f(*DARK_GREY)
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[0] + BLOCK_SIZE, pos[1])
        glVertex2f(pos[0] + BLOCK_SIZE, pos[1] + BLOCK_SIZE)
        glVertex2f(pos[0], pos[1] + BLOCK_SIZE)
