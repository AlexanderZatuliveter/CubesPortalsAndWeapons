
import sys
from typing import Tuple
import pygame
from pygame import Surface
from pygame.time import Clock
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from enemy import Enemy
from game_field import GameField
from player import Player


class MainWindow:

    def __init__(self, screen: Surface, clock: Clock) -> None:
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()
        self.__game_field = GameField(GAME_FIELD_WIDTH // BLOCK_SIZE, GAME_FIELD_HEIGHT // BLOCK_SIZE)
        self.__game_field.load_from_file()

        self.__player = Player(self.__game_field)

        self.__enemies = []

        for y in range(BLOCK_SIZE, BLOCK_SIZE * 23, BLOCK_SIZE * 4):
            self.__enemy = Enemy(
                self.__game_field,
                self.__player,
                (GAME_FIELD_WIDTH // 3 * 2, y),
                BLOCK_SIZE * 25,
                int(BLOCK_SIZE * 40.5)
            )
            self.__enemies.append(self.__enemy)

    def __resize_display(self, new_screen_size: Tuple[int, int]) -> None:
        """Handle window resizing while maintaining the aspect ratio."""

        if self.__past_screen_size == new_screen_size:
            return

        ratio_w = new_screen_size[0] / GAME_FIELD_WIDTH
        ratio_h = new_screen_size[1] / GAME_FIELD_HEIGHT

        if self.__past_screen_size[0] != new_screen_size[0] and self.__past_screen_size[1] != new_screen_size[1]:
            ratio = min(ratio_w, ratio_h)
        elif self.__past_screen_size[0] != new_screen_size[0]:
            ratio = ratio_w
        elif self.__past_screen_size[1] != new_screen_size[1]:
            ratio = ratio_h

        new_width = int(GAME_FIELD_WIDTH * ratio)
        new_height = int(GAME_FIELD_HEIGHT * ratio)

        self.__set_screen_size((new_width, new_height))

        self.__past_screen_size = pygame.display.get_window_size()

    def __set_screen_size(self, screen_size: Tuple[int, int]) -> None:
        # Set up the viewport to maintain aspect ratio
        self.__screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
        glViewport(0, 0, *screen_size)

        # Reset projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, *self.__screen.get_size(), 0, -1, 1)

    def show(self) -> None:

        self.__set_screen_size(self.__screen.get_size())

        # Set background's color
        glClearColor(100 / 255, 100 / 255, 100 / 255, 1)

        # turn on smooth lines and blending
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        while True:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Updates
            self.update(events)
            self.__player.update(keys)
            for enemy in self.__enemies:
                enemy.update()

            # Draws
            self.begin_draw()
            self.__player.draw()
            for enemy in self.__enemies:
                enemy.draw()
            self.__game_field.draw()
            self.end_draw()

    def update(self, events) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.__resize_display(event.size)

    def begin_draw(self) -> None:
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Set modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Draw things
        glBegin(GL_QUADS)

    def end_draw(self) -> None:
        glEnd()
        pygame.display.flip()
        self.__clock.tick(60)
