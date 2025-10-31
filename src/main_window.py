
import sys
from typing import Tuple
import pygame
from pygame import Surface
from pygame.time import Clock
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from consts import BLOCK_SIZE, FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, BLUE, RED, GREEN, YELLOW
from game_field import GameField
from player import Player
from renderer import Renderer


class MainWindow:

    def __init__(self, screen: Surface, clock: Clock) -> None:
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()

        self.__renderer = Renderer()

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE)
        )

        self.__game_field.load_from_file()

        joysticks_count = pygame.joystick.get_count()
        colors = [BLUE, RED, GREEN, YELLOW]

        self.__players: list[Player] = []
        for num in range(joysticks_count):
            self.__players.append(Player(self.__game_field, colors[num], num))

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
        self.__screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
        glViewport(0, 0, screen_size[0], screen_size[1])

    def show(self) -> None:
        self.__set_screen_size(self.__screen.get_size())

        # Set background's color
        glClearColor(120 / 255, 120 / 255, 120 / 255, 1)

        while True:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Updates
            self.update(events)
            for player in self.__players:
                player.update()

            # Clear once per frame, then draw all objects
            glClear(GL_COLOR_BUFFER_BIT)
            self.__renderer.use_shader()

            # Draws
            for player in self.__players:
                player.draw()

            self.__game_field.draw()

            pygame.display.flip()
            self.__clock.tick(FPS)

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
