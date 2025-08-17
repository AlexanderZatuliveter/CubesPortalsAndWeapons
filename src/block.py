from OpenGL.GL import *  # type: ignore

from consts import BLOCK_SIZE, DARK_GREY, GREY
from renderer import Renderer


class Block:
    def __init__(self, renderer: Renderer) -> None:
        self.__renderer = renderer

    def draw(self, pos: tuple[float, float]) -> None:
        self.__renderer.add_quad(pos[0], pos[1], BLOCK_SIZE, GREY)
        self.__renderer.add_outline(pos[0], pos[1], BLOCK_SIZE, DARK_GREY)
