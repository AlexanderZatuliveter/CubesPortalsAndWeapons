from typing import Tuple
import pygame
from OpenGL.GL import *  # type: ignore


class Block:
    def __init__(self) -> None:
        size = 50
        self.__rect = pygame.Rect(0, 0, size, size)

    def draw(self, pos: Tuple[int, int]) -> None:
        glColor3f(50 / 255, 50 / 255, 50 / 255)
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[0] + self.__rect.w, pos[1])
        glVertex2f(pos[0] + self.__rect.w, pos[1] + self.__rect.h)
        glVertex2f(pos[0], pos[1] + self.__rect.h)
