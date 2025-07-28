from typing import Tuple
import pygame
from OpenGL.GL import *  # type: ignore

from consts import BLOCK_SIZE, IS_DEBUG


class Block:
    def __init__(self) -> None:
        self.__rect = pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)

    def draw(self, pos: Tuple[int, int]) -> None:
        if IS_DEBUG:
            glColor3f(1, 0, 0)
            glVertex2f(pos[0] - 1, pos[1] - 1)
            glVertex2f(pos[0] + self.__rect.w + 1, pos[1] - 1)
            glVertex2f(pos[0] + self.__rect.w + 1, pos[1] + self.__rect.h + 1)
            glVertex2f(pos[0] - 1, pos[1] + self.__rect.h + 1)

        glColor3f(50 / 255, 50 / 255, 50 / 255)
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[0] + self.__rect.w, pos[1])
        glVertex2f(pos[0] + self.__rect.w, pos[1] + self.__rect.h)
        glVertex2f(pos[0], pos[1] + self.__rect.h)
