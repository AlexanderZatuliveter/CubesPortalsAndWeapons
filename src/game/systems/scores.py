from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import pygame

from engine.common import get_resource_path
from game.consts import SCORES_HEIGHT, SCORES_WIDTH
from engine.ui.text_worker import TextWorker


class Scores:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        shader: ShaderProgram | None,
        color: tuple[float, float, float]
    ) -> None:

        self.__rect: pygame.Rect = pygame.Rect(x, y, SCORES_WIDTH, SCORES_HEIGHT)
        self.__color = color
        self.__text = text
        self.__shader = shader

        self.__text_worker = TextWorker(
            x=self.__rect.x,
            y=self.__rect.y,
            text=self.__text,
            rect_size=(self.__rect.width, self.__rect.height),
            font=None,
            font_file_path=get_resource_path("src/_content/fonts/WDXLLubrifontSC-Regular.ttf"),
            shader=self.__shader,
            color=self.__color
        )

    def draw(self) -> None:
        self.__text_worker.draw()

    def update_text(self, text: str) -> None:
        self.__text = text
        self.__text_worker.update_text(text)

    def update_pos(self, x: float, y: float):
        self.__text_worker.update_pos(x, y)
