
import sys
from typing import Tuple
import pygame
from pygame import Surface
from pygame.time import Clock
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from common import create_shader, ortho
from consts import BLOCK_SIZE, FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, BLUE, RED, GREEN, YELLOW
from game_field import GameField
from player import Player


class MainWindow:

    def __init__(self, screen: Surface, clock: Clock) -> None:
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()

        # Disable unnecessary OpenGL features for 2D rendering
        glDisable(GL_DEPTH_TEST)  # No depth testing needed for 2D
        glDisable(GL_CULL_FACE)   # No backface culling needed
        glDisable(GL_MULTISAMPLE)  # No multisampling needed for pixel-perfect 2D

        self.__shader = create_shader("./src/shaders/shader.vert", "./src/shaders/shader.frag")
        glUseProgram(self.__shader)

        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
            self.__shader
        )

        self.__game_field.load_from_file()

        joysticks_count = pygame.joystick.get_count()
        colors = [BLUE, RED, GREEN, YELLOW]

        self.__players: list[Player] = []
        for num in range(joysticks_count):
            self.__players.append(Player(self.__game_field, self.__shader, colors[num], num))

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

        # Update the projection matrix in the shader
        glUseProgram(self.__shader)
        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

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

            # Draws
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.__shader)

            self.__game_field.draw()

            for player in self.__players:
                player.draw()

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
